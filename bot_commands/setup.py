import discord
from discord.ext import commands

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup", help="Sets up categories and channels for file uploads.")
    async def setup(self, ctx):
        # Create Categories (Videos, Images, Documents, etc.)
        guild = ctx.guild
        categories = ["Videos", "Images", "Documents"]
        for category_name in categories:
            existing_category = discord.utils.get(guild.categories, name=category_name)
            if not existing_category:
                await guild.create_category(category_name)
                await ctx.send(f"Created category: {category_name}")
            else:
                await ctx.send(f"Category already exists: {category_name}")

async def setup(bot):
    await bot.add_cog(Setup(bot))
