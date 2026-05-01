import AssimetricKeys 
import SymmetricCipher 
import os
import gc

class CreateDigitalEnvelope:
    def __init__(self) -> None:
        self.message = None
        #TODO: as chaves assimetricas devem ser apagadas depois do processamento 
        self.public_key = None 
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
            
            self.private_key, self.public_key = AssimetricKeys.get_rsa_keys() 
            
            if self.private_key is None or self.public_key is None:
                return False, f"Erro: os arquivos exisem mas não são do formato Pem ou estão corrompidos"
            
            return True,f"Sucesso ao carregar as chaves"
        
        except Exception as e:
            return False, f"Erro: falha na operação [{e}]"
    
    def sing_message(self):
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

    def clear_sensitive_data(self):
        self.private_key = None
        gc.collect()
