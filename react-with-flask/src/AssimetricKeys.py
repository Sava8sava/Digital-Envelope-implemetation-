from cryptography.hazmat.primitives.asymmetric import rsa 
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os
'''
Caso as chaves rsa não tenham sido criados, perderam a validade, ou corromperam, essa função gera novas chaves em arquivos PEM, é de muito importancia que a chave privada não seja vazada, esse trabalho esconde as chaves do formato pem usando gitignore, mas é bom tomar cuidado
'''

def generate_rsa_key(size_in_bits : int = 2048):
    if size_in_bits not in [1024,2048]:
        print("Erro: Tamanho de chave não aceito")
        return 
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=size_in_bits,
    )

    pem_privada = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    #xxtração e serialização da chave publica
    public_key = private_key.public_key()
    pem_publica = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    try:
        with open("private_key.pem", "wb") as f_priv:
            f_priv.write(pem_privada)
        
        with open("public_key.pem", "wb") as f_pub:
            f_pub.write(pem_publica)
            
        print(f"Sucesso! Chaves de {size_in_bits} bits geradas e salvas.")
        print("Arquivos criados: 'private_key.pem' e 'public_key.pem'")
        
    except Exception as e:
        print(f"Erro ao salvar os arquivos: {str(e)}")

def get_rsa_keys(privkey_path, pubkey_path):
    # TODO : refatorar pois esta muito hardcoded
    priv_path = privkey_path
    pub_path = pubkey_path

    private_key = None
    public_key = None

    # Verifica se os arquivos existem para evitar erro de 'Arquivo não encontrado' 
    if os.path.exists(priv_path):
        try:
            with open(priv_path, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None, #como pedido no Arquivo do trabalho, sem senha
                )
            print("Chave privada carregada com sucesso.")
        except Exception as e:
            print(f"Erro ao ler a chave privada: {e}")
    else:
        print(f"Aviso: Arquivo {priv_path} não encontrado.")

    if os.path.exists(pub_path):
        try:
            with open(pub_path, "rb") as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read(),
                )
            print("Chave pública carregada com sucesso.")
        except Exception as e:
            print(f"Erro ao ler a chave pública: {e}")
    else:
        print(f"Aviso: Arquivo {pub_path} não encontrado.")

    return private_key, public_key

def get_the_sign(private_key,message):
    try:
        signature = private_key.sign(
                message.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA512()
            )
        return True, signature 
    except Exception as e:
        return False, f"Falha na assinatura : {str(e)}"

def encrypt_session_key(public_key, combined_hex):
    try:
        data_to_encrypt = combined_hex.encode('utf-8')
        
        ciphertext_key = public_key.encrypt(
            data_to_encrypt,
            padding.PKCS1v15() # Requisito para compatibilidade com CyberChef

        )
        return True, ciphertext_key
    except Exception as e:
        return False, f"Erro:cifragem RSA não foi possivel [{str(e)}]"

def decrypt_session_key(private_key, encrypted_key):
    try:
        decrypted_bytes = private_key.decrypt(
            encrypted_key,
            padding.PKCS1v15() # o mesmo usado na cifragem 
        )
        return True, decrypted_bytes.decode('utf-8')
    except Exception as e:
        return False, f"Erro: Não foi possivel decifra a chave de sessão [{str(e)}]"

def verify_sign(public_key, message_str, signature):
    try:
        public_key.verify(
            signature,
            message_str.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA512()
        )
        return True
    except Exception:
        return False 
