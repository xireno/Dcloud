import os
import json

def split_file_into_chunks(file_path, chunk_size, temp_dir):
    """
    Splits a file into chunks of the specified size, saves them to the temp directory, 
    and generates a metadata file.

    Args:
        file_path (str): Path to the file to be split.
        chunk_size (int): Size of each chunk in bytes.
        temp_dir (str): Directory to save the chunks.

    Returns:
        list: List of chunk file paths.
    """
    os.makedirs(temp_dir, exist_ok=True)
    chunks = []
    metadata = {
        "original_file_name": os.path.basename(file_path),
        "original_file_size": os.path.getsize(file_path),
        "chunks": []
    }

    with open(file_path, "rb") as f:
        idx = 0
        while chunk := f.read(chunk_size):
            chunk_name = f"{os.path.basename(file_path)}_chunk_{idx}"
            chunk_path = os.path.join(temp_dir, chunk_name)
            with open(chunk_path, "wb") as chunk_file:
                chunk_file.write(chunk)
            chunks.append(chunk_path)
            metadata["chunks"].append(chunk_name)
            idx += 1

    # Save metadata to a JSON file
    metadata_path = os.path.join(temp_dir, f"{metadata['original_file_name']}.metadata.json")
    with open(metadata_path, "w") as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    return chunks


def combine_chunks(chunks, output_dir):
    """
    Combines chunks into a single file based on metadata.

    Args:
        chunks (list): List of chunk file paths to combine.
        output_dir (str): Directory to save the combined file.

    Returns:
        str: Path to the combined output file.
    """
    if not chunks:
        raise ValueError("No chunks provided for combination.")

    # Extract original file name from the first chunk
    metadata_file = os.path.join(os.path.dirname(chunks[0]), f"{os.path.basename(chunks[0]).split('_chunk_')[0]}.metadata.json")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

    with open(metadata_file, "r") as metadata_json:
        metadata = json.load(metadata_json)

    output_file = os.path.join(output_dir, metadata["original_file_name"])
    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "wb") as output:
        for chunk in sorted(chunks, key=lambda x: int(x.split("_chunk_")[-1])):
            with open(chunk, "rb") as f:
                output.write(f.read())

    return output_file
