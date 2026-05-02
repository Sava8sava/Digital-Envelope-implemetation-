import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
_src  = os.path.normpath(os.path.join(_here, '..', 'src'))
sys.path.insert(0, _src)

from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization
from envelope import CreateDigitalEnvelope, OpenDigitalEnvelope

app = Flask(__name__)


def load_private_key_from_content(pem_content: str):
    """Carrega chave privada diretamente do conteúdo PEM enviado pelo front."""
    return serialization.load_pem_private_key(
        pem_content.encode('utf-8'),
        password=None,
    )


def load_public_key_from_content(pem_content: str):
    """Carrega chave pública diretamente do conteúdo PEM enviado pelo front."""
    return serialization.load_pem_public_key(
        pem_content.encode('utf-8'),
    )


@app.route('/api/create-envelope', methods=['POST'])
def create_envelope():
    data = request.get_json()

    message             = data.get('message', '').strip()
    output_name         = data.get('output_name', 'output').strip() or 'output'
    private_key_content = data.get('private_key_content', '').strip()
    public_key_content  = data.get('public_key_content', '').strip()

    if not message or not private_key_content or not public_key_content:
        return jsonify({'error': 'Campos obrigatórios ausentes.'}), 400

    steps = []
    envelope = CreateDigitalEnvelope()

    # 1. Mensagem
    envelope.setMessage(message)
    steps.append({'status': 'info', 'message': 'Mensagem carregada.'})

    # 2. Carrega chaves diretamente do conteúdo PEM (sem arquivo em disco)
    try:
        envelope.private_key = load_private_key_from_content(private_key_content)
        envelope.public_key  = load_public_key_from_content(public_key_content)
        steps.append({'status': 'success', 'message': 'Chaves carregadas com sucesso.'})
    except Exception as e:
        msg = f'Erro ao carregar chaves: {str(e)}'
        steps.append({'status': 'error', 'message': msg})
        return jsonify({'error': msg, 'steps': steps}), 400

    # 3. Assinatura
    ok, signature = envelope.sign_message()
    steps.append({
        'status': 'success' if ok else 'error',
        'message': 'Mensagem assinada com sucesso.' if ok else signature
    })
    if not ok:
        return jsonify({'error': signature, 'steps': steps}), 400

    # 4. Chave de sessão e cifragem da mensagem (AES-CBC)
    combined_hex = envelope.generate_session_parameters()
    steps.append({'status': 'info', 'message': 'Parâmetros de sessão gerados (AES-CBC).'})

    ok, msg = envelope.run_message_encryptation()
    steps.append({'status': 'success' if ok else 'error', 'message': msg})
    if not ok:
        return jsonify({'error': msg, 'steps': steps}), 400

    # 5. Cifragem da chave de sessão (RSA)
    ok, encrypted_key = envelope.run_key_encryptation(combined_hex)
    steps.append({
        'status': 'success' if ok else 'error',
        'message': 'Chave de sessão cifrada com RSA.' if ok else encrypted_key
    })
    if not ok:
        return jsonify({'error': encrypted_key, 'steps': steps}), 400

    # 6. Salva os arquivos
    ok, msg = envelope.save_envelope(signature, encrypted_key, folder=output_name)
    steps.append({'status': 'success' if ok else 'error', 'message': msg})
    if not ok:
        return jsonify({'error': msg, 'steps': steps}), 400

    # 7. Limpa dados sensíveis da memória
    envelope.clear_sensitive_data()
    steps.append({'status': 'info', 'message': 'Dados sensíveis removidos da memória.'})

    return jsonify({'steps': steps, 'output_folder': output_name})


@app.route('/api/open-envelope', methods=['POST'])
def open_envelope():
    data = request.get_json()

    envelope_folder          = data.get('envelope_folder', '').strip()
    private_key_content      = data.get('private_key_content', '').strip()
    sender_public_key_content = data.get('sender_public_key_content', '').strip()

    if not envelope_folder or not private_key_content or not sender_public_key_content:
        return jsonify({'error': 'Campos obrigatórios ausentes.'}), 400

    steps = []
    decifrador = OpenDigitalEnvelope()

    # 1. Carrega os arquivos do envelope do disco
    ok, msg = decifrador.open_envelope(envelope_folder)
    steps.append({'status': 'success' if ok else 'error', 'message': msg})
    if not ok:
        return jsonify({'error': msg, 'steps': steps}), 400

    # 2. Carrega as chaves do conteúdo PEM enviado pelo front
    try:
        decifrador.private_key       = load_private_key_from_content(private_key_content)
        decifrador.sender_public_key = load_public_key_from_content(sender_public_key_content)
        steps.append({'status': 'success', 'message': 'Chaves carregadas com sucesso.'})
    except Exception as e:
        msg = f'Erro ao carregar chaves: {str(e)}'
        steps.append({'status': 'error', 'message': msg})
        return jsonify({'error': msg, 'steps': steps}), 400

    # 3. Decifra a chave de sessão
    ok, msg = decifrador.decrypt_session_key()
    steps.append({'status': 'success' if ok else 'error', 'message': msg})
    if not ok:
        return jsonify({'error': msg, 'steps': steps}), 400

    # 4. Decifra a mensagem
    ok, msg = decifrador.decrypt_message()
    steps.append({'status': 'success' if ok else 'error', 'message': msg})
    if not ok:
        return jsonify({'error': msg, 'steps': steps}), 400

    # 5. Valida a assinatura digital
    signature_valid = decifrador.is_signature_valid()
    steps.append({
        'status': 'success' if signature_valid else 'warning',
        'message': 'Assinatura digital VÁLIDA. Remetente autenticado.'
                   if signature_valid else
                   'ATENÇÃO: Assinatura INVÁLIDA. Mensagem pode ter sido adulterada.'
    })

    return jsonify({
        'steps': steps,
        'message': decifrador.decrypted_message,
        'signature_valid': signature_valid,
    })
