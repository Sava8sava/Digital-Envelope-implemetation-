from envelope import CreateDigitalEnvelope 
envelope = CreateDigitalEnvelope()
envelope.setMessage("Mensagem ultra secreta da UFPI")

# 1. Carrega Chaves
envelope.setAssimetricKeys("public_key.pem", "private_key.pem")

# 2. Assina
_, assinatura = envelope.sign_message()

# 3. Gera parâmetros e cifra mensagem (AES)
comb_hex = envelope.generate_session_parameters()
envelope.run_message_encryptation()

# 4. Cifra a chave (RSA)
_, chave_cifrada = envelope.run_key_encryptation(comb_hex)

# 5. Salva tudo
sucesso, msg = envelope.save_envelope(assinatura, chave_cifrada)
print(msg)

# 6. Limpa a memória
envelope.clear_sensitive_data()
