import os
import discord
from discord import app_commands
from discord.ext import commands
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from utils.chunking import split_file_into_chunks
from utils.compression import compress_chunk
from utils.retry import retry_with_backoff
from utils.settings import load_user_settings, save_user_settings
import asyncio


class FileSplitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_dir = "./data/temp_storage/"
        os.makedirs(self.temp_dir, exist_ok=True)

    async def get_settings(self, user_id):
        """Fetch user settings from settings file (or use defaults)."""
        return await load_user_settings(user_id)

    async def save_settings(self, user_id, settings):
        """Save user settings to the settings file."""
        await save_user_settings(user_id, settings)

    @app_commands.command(name="split_file", description="Split, compress, and upload a file.")
    async def split_file(
        self, interaction: discord.Interaction, compress: bool = None, chunk_size: str = None
    ):
        await interaction.response.send_message("Opening file selection dialog. Please wait...", ephemeral=True)

        # Fetch user settings, falling back to defaults
        settings = await self.get_settings(interaction.user.id)
        compress = compress if compress is not None else settings["compress"]
        chunk_size = chunk_size if chunk_size else settings["chunk_size"]

        # File selection dialog
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = askopenfilename(title="Select a file to split")

        if not file_path:
            await interaction.followup.send("No file selected. Operation canceled.")
            return

        # File processing
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # Chunking the file
        chunks = split_file_into_chunks(file_path, int(chunk_size), self.temp_dir)

        # Compression if selected
        if compress:
            chunks = [compress_chunk(chunk, self.temp_dir) for chunk in chunks]

        # Create categories and channels
        guild = interaction.guild
        category_name = self.get_category_by_file_type(file_name)
        category = await self.get_or_create_category(guild, category_name)
        channel_name = file_name.replace(".", "-").lower()
        channel = await self.get_or_create_channel(category, channel_name)

        # Start the progress bar in the command channel
        progress_message = await interaction.followup.send(f"Uploading chunks: 0/{len(chunks)} (0%)")

        # Upload chunks with rate-limit handling and concurrency control
        uploaded_chunks = 0
        total_chunks = len(chunks)
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent uploads

        async def upload_chunk(chunk_path, idx):
            max_retries = 5
            retry_delay = 2
            for attempt in range(max_retries):
                try:
                    message = await retry_with_backoff(lambda: channel.send(file=discord.File(chunk_path)))
                    return message.id
                except Exception as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                    else:
                        print(f"Failed to upload chunk {chunk_path} after {max_retries} attempts: {e}")
                        break

        async def upload_chunk_with_semaphore(chunk_path, idx):
            async with semaphore:
                return await upload_chunk(chunk_path, idx)

        chunk_ids = await asyncio.gather(*[upload_chunk_with_semaphore(chunk, idx) for idx, chunk in enumerate(chunks)])
        await progress_message.edit(content=f"Upload complete! {total_chunks}/{total_chunks} (100%)")

        # Determine First Chunk ID
        first_message = None
        async for message in channel.history(limit=1, oldest_first=True):
            first_message = message
        first_chunk_id = first_message.id if first_message else None

        # Determine Last Chunk ID
        last_message = None
        async for message in channel.history(limit=1):
            last_message = message
        last_chunk_id = last_message.id if last_message else None

        # Metadata storage
        metadata_md = f""" ```
File: {file_name}
Compressed: {compress}
Total Chunks: {len(chunks)}
First Chunk ID: {first_chunk_id}
Last Chunk ID: {last_chunk_id}```"""
        await channel.send(metadata_md)

        self.cleanup_temp_files(chunks)

    async def get_or_create_category(self, guild, category_name):
        """Create or get a category"""
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)
        return category

    async def get_or_create_channel(self, category, channel_name):
        """Create or get a unique channel"""
        channel = discord.utils.get(category.channels, name=channel_name)
        counter = 2
        while channel:
            new_channel_name = f"{channel_name}-{counter}"
            channel = discord.utils.get(category.channels, name=new_channel_name)
            if not channel:
                channel_name = new_channel_name
            counter += 1
        return await category.create_text_channel(channel_name)

    def get_category_by_file_type(self, file_name):
        """Determine category by file type"""
        file_type = file_name.split(".")[-1].lower()
        if file_type in ["mp4", "mkv", "avi"]:
            return "Videos"
        elif file_type in ["jpg", "jpeg", "png", "gif"]:
            return "Images"
        elif file_type in ["pdf", "docx", "txt"]:
            return "Documents"
        else:
            return "Others"

    def cleanup_temp_files(self, files):
        """Delete temporary chunk files after processing"""
        for file in files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass


async def setup(bot):
    await bot.add_cog(FileSplitter(bot))
