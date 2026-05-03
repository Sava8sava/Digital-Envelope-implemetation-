import sys
import os
import re
from datetime import datetime

_here = os.path.dirname(os.path.abspath(__file__))
_src  = os.path.normpath(os.path.join(_here, '..', 'src'))
sys.path.insert(0, _src)

from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from envelope import CreateDigitalEnvelope, OpenDigitalEnvelope

app = Flask(__name__)

# ─── Repositório de chaves ────────────────────────────────────────────────────
#
# Estrutura criada automaticamente dentro de api/ na primeira geração:
#
#   api/keys/
#     private/   ← chaves privadas  (.pem)
#     public/    ← chaves públicas  (.pem)
#
# Nomenclatura: {identidade}_{YYYYMMDD}_{HHMMSS}_{tipo}.pem
#   Exemplo:  alice_20260503_143021_private.pem
#             alice_20260503_143021_public.pem
#
KEYS_ROOT    = os.path.join(_here, 'keys')
KEYS_PRIVATE = os.path.join(KEYS_ROOT, 'private')
KEYS_PUBLIC  = os.path.join(KEYS_ROOT, 'public')


def ensure_key_dirs():
    os.makedirs(KEYS_PRIVATE, exist_ok=True)
    os.makedirs(KEYS_PUBLIC,  exist_ok=True)


def sanitize_identity(identity: str) -> str:
    clean = re.sub(r'[^\w\-]', '_', identity or 'key')
    return clean[:48].strip('_') or 'key'


def load_private_key_from_content(pem_content: str):
    return serialization.load_pem_private_key(
        pem_content.encode('utf-8'),
        password=None,
    )


def load_public_key_from_content(pem_content: str):
    return serialization.load_pem_public_key(
        pem_content.encode('utf-8'),
    )


# ─── Rota: gerar par de chaves ────────────────────────────────────────────────

@app.route('/api/generate-keys', methods=['POST'])
def generate_keys():
    data     = request.get_json()
    key_size = data.get('key_size', 2048)
    identity = sanitize_identity(data.get('identity') or '')

    if key_size not in (1024, 2048):
        return jsonify({'error': 'Tamanho de chave inválido. Use 1024 ou 2048.'}), 400

    steps = []

    try:
        ensure_key_dirs()
        steps.append({'status': 'info', 'message': f'Repositório de chaves: {KEYS_ROOT}'})
        steps.append({'status': 'info', 'message': f'Gerando par RSA de {key_size} bits...'})

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        public_key = private_key.public_key()

        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        private_filename = f'{identity}_{ts}_private.pem'
        public_filename  = f'{identity}_{ts}_public.pem'

        private_path = os.path.join(KEYS_PRIVATE, private_filename)
        public_path  = os.path.join(KEYS_PUBLIC,  public_filename)

        with open(private_path, 'wb') as f:
            f.write(pem_private)
        steps.append({'status': 'success', 'message': f'Chave privada salva: private/{private_filename}'})

        with open(public_path, 'wb') as f:
            f.write(pem_public)
        steps.append({'status': 'success', 'message': f'Chave pública salva: public/{public_filename}'})

    except Exception as e:
        msg = f'Erro ao gerar chaves: {str(e)}'
        steps.append({'status': 'error', 'message': msg})
        return jsonify({'error': msg, 'steps': steps}), 500

    return jsonify({
        'steps':            steps,
        'key_size':         key_size,
        'private_key_file': private_filename,
        'public_key_file':  public_filename,
        'private_key_path': private_path,
        'public_key_path':  public_path,
    })


# ─── Rota: criar envelope ─────────────────────────────────────────────────────

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

    envelope.setMessage(message)
    steps.append({'status': 'info', 'message': 'Mensagem carregada.'})

    try:
        envelope.private_key = load_private_key_from_content(private_key_content)
        envelope.public_key  = load_public_key_from_content(public_key_content)
        steps.append({'status': 'success', 'message': 'Chaves carregadas com sucesso.'})
    except Exception as e:
        msg = f'Erro ao carregar chaves: {str(e)}'
        steps.append({'status': 'error', 'message': msg})
        return jsonify({'error': msg, 'steps': steps}), 400

    ok, signature = envelope.sign_message()
    steps.append({
        'status': 'success' if ok else 'error',
        'message': 'Mensagem assinada com sucesso.' if ok else signature,
    })
    if not ok:
        return jsonify({'error': signature, 'steps': steps}), 400

    combined_hex = envelope.generate_session_parameters()
    steps.append({'status': 'info', 'message': 'Parâmetros de sessão gerados (AES-CBC).'})

    ok, msg = envelope.run_message_encryptation()
    steps.append({'status': 'success' if ok else 'error', 'message': msg})
    if not ok:
        return jsonify({'error': msg, 'steps': steps}), 400

    ok, encrypted_key = envelope.run_key_encryptation(combined_hex)
    steps.append({
        'status': 'success' if ok else 'error',
        'message': 'Chave de sessão cifrada com RSA.' if ok else encrypted_key,
    })
    if not ok:
        return jsonify({'error': encrypted_key, 'steps': steps}), 400

    ok, msg = envelope.save_envelope(signature, encrypted_key, folder=output_name)
    steps.append({'status': 'success' if ok else 'error', 'message': msg})
    if not ok:
        return jsonify({'error': msg, 'steps': steps}), 400

    envelope.clear_sensitive_data()
    steps.append({'status': 'info', 'message': 'Dados sensíveis removidos da memória.'})

    return jsonify({'steps': steps, 'output_folder': output_name})


# ─── Rota: abrir envelope ─────────────────────────────────────────────────────

@app.route('/api/open-envelope', methods=['POST'])
def open_envelope():
    import base64 as b64mod
    data = request.get_json()

    ciphertext_b64            = data.get('ciphertext_b64', '').strip()
    signature_b64             = data.get('signature_b64', '').strip()
    session_key_b64           = data.get('session_key_b64', '').strip()
    private_key_content       = data.get('private_key_content', '').strip()
    sender_public_key_content = data.get('sender_public_key_content', '').strip()

    if not all([ciphertext_b64, signature_b64, session_key_b64,
                private_key_content, sender_public_key_content]):
        return jsonify({'error': 'Campos obrigatórios ausentes.'}), 400

    steps = []
    decifrador = OpenDigitalEnvelope()

    # Carrega os arquivos do envelope diretamente da memória (enviados como base64)
    try:
        decifrador.ciphertext             = b64mod.b64decode(b64mod.b64decode(ciphertext_b64))
        decifrador.signature              = b64mod.b64decode(b64mod.b64decode(signature_b64))
        decifrador.encrypted_session_key  = b64mod.b64decode(b64mod.b64decode(session_key_b64))
        steps.append({'status': 'success', 'message': 'Arquivos do envelope carregados.'})
    except Exception as e:
        msg = f'Erro ao decodificar arquivos do envelope: {str(e)}'
        steps.append({'status': 'error', 'message': msg})
        return jsonify({'error': msg, 'steps': steps}), 400

    # Carrega as chaves do conteúdo PEM enviado pelo front
    try:
        decifrador.private_key       = load_private_key_from_content(private_key_content)
        decifrador.sender_public_key = load_public_key_from_content(sender_public_key_content)
        steps.append({'status': 'success', 'message': 'Chaves carregadas com sucesso.'})
    except Exception as e:
        msg = f'Erro ao carregar chaves: {str(e)}'
        steps.append({'status': 'error', 'message': msg})
        return jsonify({'error': msg, 'steps': steps}), 400

    ok, msg = decifrador.decrypt_session_key()
    steps.append({'status': 'success' if ok else 'error', 'message': msg})
    if not ok:
        return jsonify({'error': msg, 'steps': steps}), 400

    ok, msg = decifrador.decrypt_message()
    steps.append({'status': 'success' if ok else 'error', 'message': msg})
    if not ok:
        return jsonify({'error': msg, 'steps': steps}), 400

    signature_valid = decifrador.is_signature_valid()
    steps.append({
        'status': 'success' if signature_valid else 'warning',
        'message': 'Assinatura digital VÁLIDA. Remetente autenticado.'
                   if signature_valid else
                   'ATENÇÃO: Assinatura INVÁLIDA. Mensagem pode ter sido adulterada.',
    })

    return jsonify({
        'steps':           steps,
        'message':         decifrador.decrypted_message,
        'signature_valid': signature_valid,
    })
