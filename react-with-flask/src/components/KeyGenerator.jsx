import React, { useState } from 'react';

const KeyGenerator = () => {
  const [status, setStatus] = useState('Aguardando comando...');

  const handleGenerateKeys = () => {
    // Lógica de integração com o Flask será adicionada aqui futuramente
    setStatus('Gerando chaves... (Simulação)');
    setTimeout(() => {
      setStatus('Chaves geradas com sucesso e prontas para armazenamento em /keys');
    }, 1500);
  };

  return (
    <div className="key-generator-container">
      <h2>Gerenciador de Chaves Assimétricas</h2>
      <p>Utilize esta interface para gerar seu par de chaves pública e privada.</p>
      
      <div className="actions">
        <button onClick={handleGenerateKeys} className="generate-btn">
          Gerar Novo Par de Chaves
        </button>
      </div>

      <div className="status-board">
        <strong>Status:</strong> {status}
      </div>

      <div className="key-info">
        <h3>Diretórios de Destino:</h3>
        <ul>
          <li><strong>Pública:</strong> <code>react-with-flask/keys/public/</code></li>
          <li><strong>Privada:</strong> <code>react-with-flask/keys/private/</code></li>
        </ul>
      </div>
    </div>
  );
};

export default KeyGenerator;