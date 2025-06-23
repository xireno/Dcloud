import discord
import json
import os
from discord.ext import commands
from datetime import datetime


class MetadataManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = "./data/metadata/"
        os.makedirs(self.data_dir, exist_ok=True)

    def save_metadata(self, file_name, metadata):
        """
        Saves metadata to a file in the data directory.
        """
        metadata_path = os.path.join(self.data_dir, f"{file_name}_metadata.json")
        with open(metadata_path, "w") as metadata_file:
            json.dump(metadata, metadata_file, indent=4)

    def load_metadata(self, file_name):
        """
        Loads metadata for a specific file.
        """
        metadata_path = os.path.join(self.data_dir, f"{file_name}_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as metadata_file:
                return json.load(metadata_file)
        return None

    def check_expiry(self, file_name, expiry_duration_days=7):
        """
        Checks if the file is about to expire (default 7 days).
        """
        metadata = self.load_metadata(file_name)
        if metadata:
            expiry_date = datetime.strptime(metadata["expiry"], "%Y-%m-%d")
            if (expiry_date - datetime.now()).days <= expiry_duration_days:
                return True
        return False

    def update_expiry(self, file_name, new_expiry_date):
        """
        Updates the expiry date of the file.
        """
        metadata = self.load_metadata(file_name)
        if metadata:
            metadata["expiry"] = new_expiry_date
            self.save_metadata(file_name, metadata)
        return metadata


async def setup(bot):
    await bot.add_cog(MetadataManager(bot))
