
---

# ☁️ Dcloud — Exploiting Discord as a Theoretical Infinite Cloud

> **“The cloud is not a place. It’s an idea. And Discord is just another protocol.”**

Dcloud is not just software — it’s a thought experiment.  
What if storage had no rules? What if a chat app became a filesystem?

**Dcloud** bends Discord into behaving like a distributed, chunked, encrypted storage backend — building a *shadow cloud* within the seams of a social network.  
It’s an act of software graffiti. It’s S3, if S3 wore a hoodie.

---

## Overview

Dcloud isn’t a file bot. It’s a protocol hack, a proof-of-concept, and a dare:  
What if you could exploit Discord’s infrastructure to create your own infinite, distributed, encrypted cloud storage—hidden in plain sight, chunked across channels, and managed by the same platform you use to meme with friends?

**Dcloud** slices, compresses, encrypts, and uploads your files as Discord attachments—turning servers into vaults and channels into file blocks. Slash commands, parallel transfers, and metadata keep your shadow cloud organized and fast.

---

## Features

- **File Splitting:** Breaks large files into Discord-sized chunks (configurable).
- **Compression:** Optionally compresses each chunk before upload.
- **Encryption:** Optionally encrypts files before splitting (AES-256, per-file keys).
- **Parallel Upload/Download:** Fast, resilient chunk transfer with progress feedback.
- **User Settings:** Save your compression, encryption, and chunk size preferences.
- **Metadata Management:** Automated tracking for every file and chunk.
- **Category & Channel Management:** Auto-organizes files by type.
- **Resilient Transfers:** Retries and error handling built-in.
- **Slash Commands:** Modern Discord UX.

---

## File & Directory Structure

```
project-root/
│
├── main.py                # Bot entry point
├── config.py              # Basic configuration constants
├── utils/
│   ├── chunking.py        # File chunking and recombination logic
│   ├── compression.py     # Chunk compression/decompression
│   ├── encryption.py      # File encryption/decryption
│   ├── progress.py        # Terminal progress bar (optional)
│   ├── retry.py           # Retry and backoff logic
│   └── settings.py        # User settings management
│
├── bot_commands/
│   ├── file_splitter.py   # Slash command: split & upload
│   ├── file_combiner.py   # Slash command: download & recombine
│   ├── metadata.py        # Metadata management
│   ├── uploader.py        # Parallel chunk upload logic
│   └── setup.py           # Setup categories/channels
│
├── data/
│   ├── temp_storage/      # Temporary chunk storage
│   ├── combined_files/    # Final recombined files
│   ├── metadata/          # Metadata JSON files
│   └── user_settings.json # User settings storage
│
└── .env                   # Discord bot token and guild ID
```

---

## Setup & Installation

### 1. Prerequisites

- Python 3.8+
- [Discord bot token & application](https://discord.com/developers/applications)
- Required Python packages (see below)

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

Example `requirements.txt`:
```
discord.py
python-dotenv
cryptography
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_GUILD_ID=your-guild-id
```

### 4. Run the Bot

```sh
python main.py
```

---

## Usage

### 1. Initial Setup

Run the `/setup` command (if provided) to create default categories and channels for file uploads.

### 2. Splitting and Uploading a File

Use the `/split_file` slash command in Discord.  
The bot will open a file selection dialog (on the machine where the bot runs), split the file, and upload the chunks to a dedicated text channel.

**Options:**
- `compress`: Whether to compress each chunk before uploading.
- `chunk_size`: Size of each chunk (in bytes).

**Process:**
- The bot splits the file into chunks.
- Optionally compresses/encrypts each chunk.
- Uploads each chunk to a newly created text channel under the appropriate category (Videos, Images, Documents, Others).
- Posts a metadata message in the channel with info needed for recombination.

### 3. Downloading and Recombining a File

Use the `/combine_file` slash command and provide the channel ID where the chunks were uploaded.

**Process:**
- The bot reads the metadata message in the channel.
- Downloads all the chunks in parallel.
- Recombines them into the original file.
- Saves the file to the `data/combined_files/` directory on the bot host.

### 4. User Settings

User preferences for compression, encryption, and chunk size are saved per user in `data/user_settings.json` and can be reused for subsequent operations.

---

## Advanced Features

- **Encryption:** AES-256 in CFB mode. Keys are generated per file unless specified.
- **Compression:** zlib for chunk compression.
- **Retry Logic:** Automatic retries for uploads/downloads with exponential backoff.
- **Progress Reporting:** Real-time progress updates in Discord during uploads/downloads.
- **Metadata Management:** Metadata is posted in Discord and stored locally for expiry tracking.

---

## Security Notes

- Encryption keys, if generated, must be securely stored and shared with authorized users. The bot does not manage key distribution.
- Files are processed and stored temporarily on the machine running the bot. Ensure adequate disk space and security.

---

## Limitations

- File selection dialog (`tkinter`) only works on the machine where the bot is running.
- Only supports splitting and recombining files via Discord; does not provide public file hosting.
- Maximum file size is limited by available disk space and Discord rate limits.

---

## Contributing

Pull requests and issues welcome. If you have ideas for new exploits, optimizations, or features, let’s push the boundaries together.

---

## Credits

- Built using [discord.py](https://github.com/Rapptz/discord.py)
- Uses [cryptography](https://cryptography.io/) for encryption

---

> “Storage is a story we tell the future about what mattered to us.”

---

**Dcloud: The cloud isn’t a place. It’s a possibility.**
