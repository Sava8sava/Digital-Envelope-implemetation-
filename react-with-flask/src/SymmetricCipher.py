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

def decrypt_message(ciphertext, key, iv):
    try:
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_msg = decryptor.update(ciphertext) + decryptor.finalize()

        # REMOVE O PADDING PKCS7
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_msg) + unpadder.finalize()

        return True, plaintext.decode('utf-8')
    except Exception as e:
        return False, f"Erro: não foi possivel decifrar a mensagem: [{str(e)}]"
