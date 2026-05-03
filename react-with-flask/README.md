# Implementação de Envelope Digital

Este repositório contém a implementação de um sistema de **Envelope Digital**, demonstrando a aplicação prática de conceitos essenciais de segurança da informação e criptografia, incluindo confidencialidade, integridade, autenticação e não repúdio.

---

## 🛠️ Tecnologias Utilizadas

A arquitetura da aplicação foi desenhada dividindo as responsabilidades entre o cliente (interface) e o servidor (processamento criptográfico):

* **Frontend**: Desenvolvido utilizando **React** juntamente com **Vite**. Esta combinação garante uma interface de usuário rápida, moderna e componentizada para facilitar as interações com os arquivos e formulários.
* **Backend / API**: Construído com **Flask** (Python). O Flask funciona como a API RESTful que conecta o Frontend em React aos módulos de criptografia no backend. Ele expõe rotas (como `/api/generate-keys`, `/api/create-envelope`, `/api/open-envelope`) para processar as requisições com segurança.
* **Criptografia**: Utilização da biblioteca `cryptography` nativa do ecossistema Python (módulos `hazmat`) para garantir o uso de primitivas criptográficas padronizadas e seguras.

---

## 🔐 Recursos de Segurança e Criptografia

A aplicação busca implementar recursos robustos de segurança para fins de teste e estudo, combinando criptografia simétrica e assimétrica na formação de um envelope digital completo:

* **Criptografia Simétrica (AES-CBC)**: Utilizada para cifrar a mensagem real do usuário. Para cada envelope, o sistema gera aleatoriamente (`os.urandom`) uma nova Chave de Sessão de 128 bits e um Vetor de Inicialização (IV). O preenchimento dos blocos utiliza **PKCS7**.
* **Criptografia Assimétrica (RSA)**: Utilizada para o transporte seguro da Chave de Sessão. Suporta a geração de chaves de **1024 ou 2048 bits**. A chave de sessão AES é cifrada com a Chave Pública do destinatário utilizando o esquema de preenchimento **PKCS1v15**.
* **Assinatura Digital (RSA + SHA-512)**: Garante a autenticidade e a integridade da mensagem (não repúdio). A mensagem em texto claro passa por uma função de hash SHA-512 e é assinada com a Chave Privada do remetente antes do empacotamento.
* **Limpeza de Memória (Segurança em execução)**: A aplicação se preocupa com os dados em memória, possuindo métodos (`clear_sensitive_data()`) e acionando o *Garbage Collector* para remover chaves privadas da RAM após o uso imediato.

---

## 💻 Funcionalidades (Nível de Usuário)

Através da interface interativa, o usuário pode realizar o ciclo completo da troca de mensagens seguras:

1.  **Geração de Chaves RSA**: 
    * Permite a criação de um novo par de chaves (Pública e Privada), atribuindo uma "identidade" (ex: Alice, Bob).
    * O sistema exporta automaticamente os arquivos no formato padrão de codificação `.pem`.
2.  **Criação do Envelope Digital (Envio)**:
    * O remetente digita uma mensagem secreta de texto.
    * Carrega a sua **Chave Privada** (usada pelo sistema para gerar a assinatura digital).
    * Carrega a **Chave Pública do Destinatário** (usada pelo sistema para cifrar a chave de sessão).
    * Como saída, o sistema gera e baixa os componentes do envelope em Base64: a mensagem cifrada (`.cif`), a assinatura digital (`.sig`) e a chave de sessão criptografada (`.env`).
3.  **Abertura do Envelope Digital (Recebimento)**:
    * O destinatário carrega os três arquivos que formam o envelope (`mensagem.cif`, `signature.sig`, `session_key.env`).
    * Fornece a sua **Chave Privada** (para conseguir decifrar a chave de sessão AES).
    * Fornece a **Chave Pública do Remetente** (para que o sistema possa validar a assinatura digital original).
    * A aplicação exibe o texto decifrado na tela e apresenta um **status de segurança visual**, informando de maneira clara se a Assinatura Digital é **Válida** (remetente autenticado) ou se apresenta algum alerta de adulteração.
