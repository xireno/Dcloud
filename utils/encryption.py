from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


def encrypt_file(file_path, output_dir, key=None, iv=None):
    """
    Encrypts the file at `file_path` and saves the encrypted file to the `output_dir`.
    """
    if not key:
        key = os.urandom(32)  # AES key (256-bit)
    if not iv:
        iv = os.urandom(16)  # AES initialization vector (128-bit)

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    encryptor = cipher.encryptor()

    encrypted_file_path = os.path.join(output_dir, os.path.basename(file_path) + ".enc")
    with open(file_path, 'rb') as f:
        file_data = f.read()

    encrypted_data = encryptor.update(file_data) + encryptor.finalize()

    with open(encrypted_file_path, 'wb') as encrypted_file:
        encrypted_file.write(iv + encrypted_data)

    return encrypted_file_path


def decrypt_file(file_path, output_dir, key=None, iv=None):
    """
    Decrypts the file at `file_path` and saves the decrypted file to the `output_dir`.
    """
    with open(file_path, 'rb') as f:
        iv_and_data = f.read()

    iv = iv_and_data[:16]
    encrypted_data = iv_and_data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    decrypted_file_path = os.path.join(output_dir, os.path.basename(file_path).replace(".enc", ""))
    with open(decrypted_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

    return decrypted_file_path
