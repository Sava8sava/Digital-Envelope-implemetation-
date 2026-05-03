import AssimetricKeys 
import SymmetricCipher 
import base64
import os
import gc

class CreateDigitalEnvelope:
    def __init__(self) -> None:
        self.message = None
        #TODO: as chaves assimetricas devem ser apagadas depois do processamento 
        self.public_key = None #o caminho da chave publica é a do destinatario não a do remetente 
        self.private_key = None 
        self.session_key = None
        self.iv = None
        self.ciphertext = None 

    def setMessage(self,message : str) -> None:
        self.message = message
    
    def setAssimetricKeys(self, pubk_path : str, privk_path : str):
        try:
            if not os.path.exists(pubk_path) or not os.path.exists(privk_path):
                return False, f"Erro: Path dos arquivos de chave não existem"
            
            self.private_key, self.public_key = AssimetricKeys.get_rsa_keys(privk_path,pubk_path) 
            
            if self.private_key is None or self.public_key is None:
                return False, f"Erro: os arquivos exisem mas não são do formato Pem ou estão corrompidos"
            
            return True,f"Sucesso ao carregar as chaves"
        
        except Exception as e:
            return False, f"Erro: falha na operação [{e}]"
    
    def sign_message(self):
        if self.private_key is None or not self.message:
            return False, f"Erro: Sua chave privada ou sua mensagem estão vazias"
        
        status,signature = AssimetricKeys.get_the_sign(self.private_key,self.message)

        return status,signature
    
    def generate_session_parameters(self):
        ''' urandom é uma função do tipo random focada em uso criptografico'''
        key = os.urandom(16)
        iv = os.urandom(16)

        self.session_key = key 
        self.iv = iv
        
        combined_hex = key.hex() + iv.hex()
        return combined_hex 
    
    def run_message_encryptation(self):
        if not self.message:
            return False, "Erro:Mensagem vazia"
        if not self.session_key or not self.iv:
            return False, "Erro:Chave de sessão ou vetor de inicialização estão vazios"

        status, result = SymmetricCipher.encrypt_message(self.message, self.session_key, self.iv)
        if status:
            self.ciphertext = result
            return True,"Sucesso: mensagem cifrada"
        return False, result
    
    def run_key_encryptation(self,combined_hex):
        if self.public_key is None:
            return False, "Erro: Chave publica esta vazia"

        status, result = AssimetricKeys.encrypt_session_key(self.public_key,combined_hex)

        if status:
            return True, result
        return False, result 
    
    #todo: o usuario pode definir o nome da mensagem 
    def save_envelope(self, signature, encrypted_key, folder = "output"):
        if not self.ciphertext:
            return False,"Erro: texto cifrado não encontrado"

        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
            
            #todo: ter que refatorar isso no futuro para testar com o cyberchef
            paths = {
                "ciphertext" : os.path.join(folder,"mensagem.cif"),
                "Digital_signature" : os.path.join(folder,"signature.sig"),
                "key" : os.path.join(folder, "session_key.env")
            }

            with open(paths["ciphertext"], "wb") as f:
                f.write(base64.b64encode(self.ciphertext))

            # Assinatura Digital (RSA)
            with open(paths["Digital_signature"], "wb") as f:
                f.write(base64.b64encode(signature))

            # Chave de Sessão Cifrada (RSA)
            with open(paths["key"], "wb") as f:
                f.write(base64.b64encode(encrypted_key))           
    
            return True, f"Sucesso: arquivos salvos na pasta {folder}"
        except Exception as e:
            return False, f"Erro: não foi possivel salvar os arquivos [{e}]"

    def clear_sensitive_data(self):
        self.private_key = None
        gc.collect()

class OpenDigitalEnvelope:
    def __init__(self) -> None:
        self.ciphertext = None 
        self.decrypted_message = None
        self.encrypted_session_key= None 
        self.decrypted_session_key= None
        self.decrypted_iv = None 
        self.signature = None 
        self.private_key = None
        self.sender_public_key = None 

    def open_envelope(self,folder_path):
        # TODO: mudar essa parte no futuro para funcionar no cyberchef, muito hardcoded
        try:
            with open(os.path.join(folder_path, "mensagem.cif"), "rb") as f:
                self.ciphertext = base64.b64decode(f.read())
            
            with open(os.path.join(folder_path, "signature.sig"), "rb") as f:
                self.signature = base64.b64decode(f.read())
                
            with open(os.path.join(folder_path, "session_key.env"), "rb") as f:
                self.encrypted_session_key = base64.b64decode(f.read())
            
            return True,"Sucesso: arquivos carregados"
        
        except Exception as e:
            return False, f"Erro: Não foi possivel abrir os arquivos: [{e}]"
    
    # essa função abre a chave privada de quem recebeu e abre a chave publica de quem enviou
    def set_keys(self,reciver_privkey_path,sender_pubkey_path):
        try:
            if not os.path.exists(reciver_privkey_path) or not os.path.exists(sender_pubkey_path):
                return False, f"Erro: Path dos arquivos de chave não existem"
            
            self.private_key, self.sender_public_key = AssimetricKeys.get_rsa_keys(reciver_privkey_path,sender_pubkey_path) 
            
            if self.private_key is None or self.sender_public_key is None:
                return False, f"Erro: os arquivos exisem mas não são do formato Pem ou estão corrompidos"
            
            return True,f"Sucesso ao carregar as chaves"
        
        except Exception as e:
            return False, f"Erro: falha na operação [{e}]"

    def decrypt_session_key(self):
        #recuperação da chave de sessão 
        status_rsa, combined_hex = AssimetricKeys.decrypt_session_key(
            self.private_key, self.encrypted_session_key
        )
        if not status_rsa: 
            return False, combined_hex

        #divisão da chave e do iv 
        try:
            session_key_hex = combined_hex[:32]
            iv_hex = combined_hex[32:]
            
            key_bytes = bytes.fromhex(session_key_hex)
            iv_bytes = bytes.fromhex(iv_hex)
            
            self.decrypted_session_key, self.decrypted_iv = key_bytes, iv_bytes
            return True, "Sucesso: Chave de sessão decifrada"
        except Exception:
            return False, "Erro: não foi possivel processar o formato Hexadecimal da chave"

    def decrypt_message(self):
        if self.decrypted_session_key is None or self.decrypted_iv is None:
            return False, "Erro: Chave de sessão e/ou iv vazios"

        status_aes, result = SymmetricCipher.decrypt_message(
            self.ciphertext, self.decrypted_session_key, self.decrypted_iv
        )
        
        if status_aes:
            self.decrypted_message = result
            # print(self.decrypted_message)
            return True, "Sucesso: Messagem decifrada"
        return False, result

    def is_signature_valid(self):
        return AssimetricKeys.verify_sign(self.sender_public_key,self.decrypted_message,self.signature) 
