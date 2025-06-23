import os
import zlib


def compress_chunk(chunk_path, temp_dir):
    """
    Compress a chunk and save it to the temp directory.
    """
    compressed_path = os.path.join(temp_dir, f"{os.path.basename(chunk_path)}.gz")
    with open(chunk_path, "rb") as f_in, open(compressed_path, "wb") as f_out:
        f_out.write(zlib.compress(f_in.read()))
    return compressed_path


def decompress_chunk(chunk_path, temp_dir):
    """
    Decompress a chunk and save it to the temp directory.
    """
    decompressed_path = os.path.join(temp_dir, os.path.basename(chunk_path).replace(".gz", ""))
    with open(chunk_path, "rb") as f_in, open(decompressed_path, "wb") as f_out:
        f_out.write(zlib.decompress(f_in.read()))
    return decompressed_path
