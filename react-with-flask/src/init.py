import os
import subprocess
import venv
import sys

def main():
    # Define o diretório base do projeto como o diretório atual de onde o script está sendo rodado
    # Recomenda-se colocar este init.py dentro da pasta react-with-flask
    base_dir = os.path.abspath(os.path.dirname(__file__))
    venv_dir = os.path.join(base_dir, 'venv')

    print("=== Iniciando a Configuração Automatizada do Projeto Envelope Digital ===")

    # 1. Criação do Ambiente Virtual (venv)
    print("\n[1/5] Criando o ambiente virtual Python (venv)...")
    if not os.path.exists(venv_dir):
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(venv_dir)
        print("Ambiente virtual criado com sucesso.")
    else:
        print("Ambiente virtual já existente. Pulando criação.")

    # Ajuste de executáveis conforme o sistema operacional (Windows vs Linux/Mac)
    if os.name == 'nt':
        pip_exe = os.path.join(venv_dir, 'Scripts', 'pip.exe')
        python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe')
        npm_cmd = 'npm.cmd'
    else:
        pip_exe = os.path.join(venv_dir, 'bin', 'pip')
        python_exe = os.path.join(venv_dir, 'bin', 'python')
        npm_cmd = 'npm'

    # 2. Instalação das dependências do Backend (Python)
    print("\n[2/5] Instalando as dependências do backend no venv (Flask, cryptography)...")
    try:
        # Adicionando flask-cors pois é essencial para a comunicação entre React e Flask rodando em portas diferentes
        subprocess.run([pip_exe, 'install', 'flask', 'cryptography', 'flask-cors'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar pacotes Python: {e}")
        sys.exit(1)

    # 3. Instalação das dependências do Frontend (Node.js)
    print("\n[3/5] Instalando dependências do Node (npm install)...")
    try:
        subprocess.run([npm_cmd, 'install'], cwd=base_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar npm install: {e}")
        sys.exit(1)

    # 4. Executando o Build do Frontend
    print("\n[4/5] Executando o build do projeto (npm run build)...")
    try:
        subprocess.run([npm_cmd, 'run', 'build'], cwd=base_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o build: {e}")
        sys.exit(1)

    # 5. Iniciando os Serviços Concorrentemente (Frontend + Backend)
    print("\n[5/5] === Configuração Concluída! Iniciando servidores... ===")
    print("Os logs do React (dev) e do Flask (api) aparecerão abaixo.")
    print("Pressione Ctrl+C a qualquer momento para desligar os servidores.")
    
    frontend_process = None
    backend_process = None

    try:
        # Inicia o frontend em background
        frontend_process = subprocess.Popen([npm_cmd, 'run', 'dev'], cwd=base_dir)

        # Inicia o backend. 
        # Utilizamos subprocess.Popen para rodar 'npm run api'.
        # DICA: Certifique-se que o seu package.json executa o Python de dentro da VENV 
        # Ex: "api": ".\\venv\\Scripts\\python api/api.py" ou equivalente.
        backend_process = subprocess.Popen([npm_cmd, 'run', 'api'], cwd=base_dir)

        # Mantém o script principal rodando enquanto os subprocessos existem
        frontend_process.wait()
        backend_process.wait()

    except KeyboardInterrupt:
        print("\nEncerrando servidores de forma segura...")
        if frontend_process:
            frontend_process.terminate()
        if backend_process:
            backend_process.terminate()
        print("Servidores desligados. Até a próxima!")

if __name__ == '__main__':
    main()
