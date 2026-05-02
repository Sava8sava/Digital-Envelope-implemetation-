import { useState } from 'react'
import StatusLog from './StatusLog'
import FileInput from './FileInput'

const INITIAL_STATE = {
  envelopeFolder: '',
  privateKeyPath: '',
  senderPublicKeyPath: '',
}

function OpenEnvelope() {
  const [form, setForm] = useState(INITIAL_STATE)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const addLog = (status, message) => {
    setLogs(prev => [...prev, { status, message, id: Date.now() + Math.random() }])
  }

  const handleChange = (field) => (e) => {
    setForm(prev => ({ ...prev, [field]: e.target.value }))
  }

  const handleSubmit = async () => {
    const { envelopeFolder, privateKeyPath, senderPublicKeyPath } = form

    if (!envelopeFolder || !privateKeyPath || !senderPublicKeyPath) {
      addLog('error', 'Erro: Preencha todos os campos obrigatórios.')
      return
    }

    setLogs([])
    setLoading(true)
    setResult(null)

    try {
      addLog('info', 'Iniciando processo de abertura do envelope...')

      const response = await fetch('/api/open-envelope', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          envelope_folder: envelopeFolder,
          private_key_content: privateKeyPath,
          sender_public_key_content: senderPublicKeyPath,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        addLog('error', data.error || 'Erro desconhecido ao abrir o envelope.')
        return
      }

      data.steps?.forEach(step => addLog(step.status, step.message))
      setResult(data)
    } catch (err) {
      addLog('error', `Erro de conexão com o servidor: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setForm(INITIAL_STATE)
    setLogs([])
    setResult(null)
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <h2 className="panel-title">ABRIR ENVELOPE</h2>
        <p className="panel-desc">
          Decifra a chave de sessão com RSA, recupera a mensagem via AES-CBC e valida a assinatura digital.
        </p>
      </div>

      <div className="form-grid">
        <div className="field full-width">
          <label className="field-label">
            <span className="field-num">01</span> PASTA DO ENVELOPE
            <span className="required">*</span>
          </label>
          <input
            className="field-input"
            type="text"
            placeholder="Caminho da pasta com os arquivos do envelope..."
            value={form.envelopeFolder}
            onChange={handleChange('envelopeFolder')}
            disabled={loading}
          />
          <span className="field-hint">Deve conter: mensagem.cif · signature.sig · session_key.env</span>
        </div>

        <FileInput
          num="02"
          label="CHAVE PRIVADA (Destinatário)"
          required
          value={form.privateKeyPath}
          onChange={handleChange('privateKeyPath')}
          disabled={loading}
          hint="Usada para decifrar a chave de sessão"
        />

        <FileInput
          num="03"
          label="CHAVE PÚBLICA (Remetente)"
          required
          value={form.senderPublicKeyPath}
          onChange={handleChange('senderPublicKeyPath')}
          disabled={loading}
          hint="Usada para validar a assinatura digital"
        />
      </div>

      <div className="action-row">
        <button
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <><span className="spinner" /> PROCESSANDO...</>
          ) : (
            <> ABRIR ENVELOPE</>
          )}
        </button>
        <button
          className="btn btn-ghost"
          onClick={handleReset}
          disabled={loading}
        >
          LIMPAR
        </button>
      </div>

      {logs.length > 0 && (
        <StatusLog logs={logs} success={result !== null} />
      )}

      {result && (
        <div className="result-box">
          <div className="result-header">
            <span className="result-label">MENSAGEM DECIFRADA</span>
            <SignatureBadge valid={result.signature_valid} />
          </div>
          <pre className="result-message">{result.message}</pre>
        </div>
      )}
    </div>
  )
}

function SignatureBadge({ valid }) {
  return (
    <span className={`signature-badge ${valid ? 'valid' : 'invalid'}`}>
      {valid ? '✓ ASSINATURA VÁLIDA' : '✗ ASSINATURA INVÁLIDA'}
    </span>
  )
}

export default OpenEnvelope
