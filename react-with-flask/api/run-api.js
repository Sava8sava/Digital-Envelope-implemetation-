import { platform } from 'os';
import { execSync } from 'child_process';

const osType = platform(); // 'win32' para Windows, 'darwin' para Mac, 'linux' para Linux
const port = process.env.API_PORT || 8080;

let command;

if (osType === 'win32') {
    command = 'cd api && venv\\Scripts\\python -m flask --app api.py run --no-debugger --port ' + port;
} else {
    command = 'cd api && venv/bin/python -m flask --app api.py run --no-debugger --port ' + port;
}

console.log(`Iniciando API para o sistema: ${osType}, na porta ${port}`);

try {
    // stdio: 'inherit' garante que os logs do Flask apareçam no terminal do usuário
    execSync(command, { stdio: 'inherit' });
} catch (error) {
    console.error("Erro ao iniciar a API:", error.message);
    process.exit(1);
}