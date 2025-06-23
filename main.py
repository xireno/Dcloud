import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

# Configure bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    """
    Event: Fired when the bot is ready and connected to Discord.
    """
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"Bot logged in as {bot.user.name} ({bot.user.id})")
        print(f"Connected to guild: {guild.name} ({guild.id})")
    else:
        print(f"Bot logged in as {bot.user.name} ({bot.user.id})")
        print(f"Warning: Guild with ID {GUILD_ID} not found!")


@bot.event
async def setup_hook():
    """
    Event: Setup hook to load commands from bot_commands folder and sync slash commands.
    """
    guild = discord.Object(id=GUILD_ID)

    # Load all extensions in the bot_commands folder
    for filename in os.listdir("./bot_commands"):
        if filename.endswith(".py") and filename != "__init__.py":
            extension_name = f"bot_commands.{filename[:-3]}"
            try:
                await bot.load_extension(extension_name)
                print(f"Loaded {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

    # Sync slash commands to the guild
    try:
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Slash commands synced to guild {GUILD_ID}: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"Error syncing commands: {e}")


# Run the bot
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"Error starting bot: {e}")
