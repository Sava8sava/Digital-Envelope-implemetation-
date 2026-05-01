from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def encrypt_message(clear_text : str, key_bytes, iv_bytes):
    try:
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(clear_text.encode()) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return True, ciphertext
    except Exception as e:
        return False, str(e)



