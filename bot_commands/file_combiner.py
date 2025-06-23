import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands


class FileCombiner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.combined_dir = os.path.join(self.base_dir, "../data/combined_files")
        self.temp_dir = os.path.join(self.base_dir, "../data/temp_storage")
        os.makedirs(self.combined_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def parse_metadata(self, metadata_message):
        """
        Parse metadata from the Discord markdown message content.
        """
        metadata_lines = metadata_message.content.strip("```").splitlines()
        metadata = {}
        for line in metadata_lines:
            if not line.strip() or ":" not in line:
                continue
            try:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
            except ValueError as e:
                raise Exception(f"Failed to parse metadata line: {line}. Error: {e}")
        return metadata

    async def retry_chunk_download(self, attachment, retries=3, delay=1):
        """
        Retry downloading a chunk up to 'retries' times with exponential backoff.
        """
        for attempt in range(retries):
            try:
                chunk_path = os.path.join(self.temp_dir, attachment.filename)
                await attachment.save(chunk_path)
                return chunk_path
            except Exception as e:
                print(f"Failed to download chunk (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
        raise Exception(f"Failed to download chunk after {retries} attempts.")

    async def download_chunks_with_parallelism(self, first_id, last_id, chunk_channel, interaction):
        """
        Download chunks with parallelism and progress updates.
        """
        chunks = []
        total_chunks = last_id - first_id + 1
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent downloads

        progress_message = await interaction.edit_original_response(content="Downloading chunks: `[                    ] 0%`")

        # Helper function to download a single chunk
        async def download_single_chunk(idx, message):
            async with semaphore:
                try:
                    attachment = message.attachments[0]
                    chunk_path = os.path.join(self.temp_dir, attachment.filename)
                    await attachment.save(chunk_path)
                    chunks.append(chunk_path)

                    # Update progress
                    percent = int(((idx + 1) / total_chunks) * 100)
                    progress_bar = ("█" * (percent // 5)).ljust(20)
                    await progress_message.edit(content=f"Downloading chunks: `[{progress_bar}] {percent}%`")
                except Exception as e:
                    print(f"Failed to process chunk attachment: {e}")

        # Collect messages into a list for parallel processing
        messages = [
            message
            async for message in chunk_channel.history(after=discord.Object(id=first_id - 1), before=discord.Object(id=last_id + 1))
        ]

        # Download chunks in parallel
        tasks = [download_single_chunk(idx, message) for idx, message in enumerate(reversed(messages))]
        await asyncio.gather(*tasks)

        await progress_message.edit(content="✅ Download complete!")
        return sorted(chunks, key=lambda x: int(x.split("_chunk_")[-1]))

    async def combine_chunks(self, chunks, output_file):
        """
        Combine chunks into a single file.
        """
        with open(output_file, "wb") as output:
            for chunk_path in chunks:
                with open(chunk_path, "rb") as chunk:
                    output.write(chunk.read())
        return output_file

    @app_commands.command(name="combine_file", description="Combine file chunks using metadata in the channel.")
    async def combine_file(self, interaction: discord.Interaction, channel_id: str):
        """
        Combine file chunks by providing the channel ID.
        """
        await interaction.response.send_message("Starting file retrieval process. Please wait...", ephemeral=True)

        try:
            # Get the target channel
            channel = interaction.guild.get_channel(int(channel_id))
            if not channel:
                raise Exception("Channel not found.")

            # Fetch and parse metadata from the channel
            metadata_message = await self.get_metadata_from_channel(channel)
            metadata = self.parse_metadata(metadata_message)

            # Validate metadata
            required_keys = ["File", "First Chunk ID", "Last Chunk ID"]
            for key in required_keys:
                if key not in metadata:
                    raise Exception(f"Metadata is missing the required field: {key}")

            first_id = int(metadata["First Chunk ID"])
            last_id = int(metadata["Last Chunk ID"])

            if first_id > last_id:
                raise Exception("First Chunk ID is greater than Last Chunk ID.")

            # Download chunks
            chunks = await self.download_chunks_with_parallelism(first_id, last_id, channel, interaction)

            # Combine chunks
            output_file = os.path.join(self.combined_dir, metadata["File"])
            combined_file = await self.combine_chunks(chunks, output_file)

            # Cleanup chunks
            for chunk in chunks:
                os.remove(chunk)

            # Notify user of completion
            await interaction.edit_original_response(
                content=f"File successfully combined and saved locally at:\n`{combined_file}`"
            )

        except Exception as e:
            await interaction.edit_original_response(content=f"Error: {e}")

    async def get_metadata_from_channel(self, channel):
        """
        Fetch the metadata message (assumed to be the last message in the channel).
        """
        async for message in channel.history(limit=10):
            if message.content.startswith("```") and "File:" in message.content:
                return message
        raise Exception("Metadata message not found in the channel.")


async def setup(bot):
    await bot.add_cog(FileCombiner(bot))
