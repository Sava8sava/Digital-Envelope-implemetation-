from envelope import OpenDigitalEnvelope
import os

# Inicializa o objeto de abertura
decifrador = OpenDigitalEnvelope()

print("--- Iniciando Processo de Abertura do Envelope ---")

# 1. Carregar os arquivos do disco (Pasta 'output' gerada no teste anterior)
# O método open_envelope lê os arquivos .cif, .sig e .env e faz o b64decode
sucesso_load, msg_load = decifrador.open_envelope("output")
print(msg_load)

if sucesso_load:
    # 2. Carregar as chaves necessárias
    # IMPORTANTE: Aqui você usa a SUA privada (para abrir a chave de sessão)
    # e a PÚBLICA do remetente (para validar a assinatura)
    # Como você usou as mesmas chaves no teste, passamos os mesmos caminhos
    sucesso_keys, msg_keys = decifrador.set_keys("private_key.pem", "public_key.pem")
    print(msg_keys)

    if sucesso_keys:
        # 3. Decifrar a chave de sessão (RSA)
        # Recupera o combined_hex e separa em Key e IV
        sucesso_session, msg_session = decifrador.decrypt_session_key()
        print(msg_session)

        if sucesso_session:
            # 4. Decifrar a mensagem real (AES-CBC)
            sucesso_msg, msg_final = decifrador.decrypt_message()
            
            if sucesso_msg:
                print(f"\n[SUCESSO] Mensagem Decifrada: {msg_final}")

                # 5. Verificar a integridade (Assinatura Digital)
                if decifrador.is_signature_valid():
                    print("[SEGURANÇA] Assinatura VALIDADA. O remetente é autêntico.")
                else:
                    print("[PERIGO] Assinatura INVÁLIDA. A mensagem pode ter sido alterada!")
            else:
                print(f"[ERRO] Falha na decifragem AES: {msg_final}")
        else:
            print(f"[ERRO] Falha no RSA: {msg_session}")
    else:
        print(f"[ERRO] Chaves não encontradas: {msg_keys}")
else:
    print(f"[ERRO] Falha ao carregar arquivos: {msg_load}")

print("\n--- Fim do Processo ---")
