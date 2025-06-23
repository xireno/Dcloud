import asyncio
import discord
from discord.ext import commands
from utils.retry import retry_with_backoff
from utils.progress import display_progress


class Uploader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def upload_chunk_with_progress(self, chunk_path, channel, idx, total_chunks, progress_message):
        """
        Upload a chunk with progress tracking.
        """
        try:
            await retry_with_backoff(
                lambda: channel.send(file=discord.File(chunk_path))
            )
            progress = int(((idx + 1) / total_chunks) * 100)
            await progress_message.edit(content=f"Uploading chunks: {idx + 1}/{total_chunks} ({progress}%)")
        except Exception as e:
            await progress_message.edit(content=f"Error uploading chunk {idx + 1}/{total_chunks}: {str(e)}")

    async def parallel_upload_chunks(self, chunks, channel):
        """
        Upload all chunks in parallel.
        """
        total_chunks = len(chunks)
        progress_message = await channel.send(f"Uploading chunks: 0/{total_chunks} (0%)")

        tasks = []
        for idx, chunk in enumerate(chunks):
            tasks.append(self.upload_chunk_with_progress(chunk, channel, idx, total_chunks, progress_message))

        await asyncio.gather(*tasks)

        # Once all chunks are uploaded, finalize the progress message
        await progress_message.edit(content=f"Upload complete! {total_chunks}/{total_chunks} (100%)")

    @commands.command(name="upload_chunks", help="Uploads file chunks to the designated channel.")
    async def upload_chunks(self, ctx, channel_id: int, chunks: list):
        """
        Upload file chunks to a specified channel with real-time progress.
        """
        try:
            guild = ctx.guild
            channel = guild.get_channel(channel_id)

            if not channel:
                await ctx.send("Invalid channel ID provided.")
                return

            # Start parallel upload
            await self.parallel_upload_chunks(chunks, channel)

            await ctx.send("All chunks uploaded successfully!")

        except Exception as e:
            await ctx.send(f"Error uploading chunks: {e}")


async def setup(bot):
    await bot.add_cog(Uploader(bot))
