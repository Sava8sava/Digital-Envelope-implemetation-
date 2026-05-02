import { useState } from 'react'
import StatusLog from './StatusLog'
import FileInput from './FileInput'

const INITIAL_STATE = {
  message: '',
  outputName: '',
  privateKeyPath: '',
  publicKeyPath: '',
}

function CreateEnvelope() {
  const [form, setForm] = useState(INITIAL_STATE)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const addLog = (status, message) => {
    setLogs(prev => [...prev, { status, message, id: Date.now() + Math.random() }])
  }

  const handleChange = (field) => (e) => {
    setForm(prev => ({ ...prev, [field]: e.target.value }))
  }

  const handleSubmit = async () => {
    const { message, outputName, privateKeyPath, publicKeyPath } = form

    if (!message || !privateKeyPath || !publicKeyPath) {
      addLog('error', 'Erro: Mensagem e ambas as chaves são obrigatórias.')
      return
    }

    setLogs([])
    setLoading(true)
    setSuccess(false)

    try {
      addLog('info', 'Iniciando processo de criação do envelope...')

      const response = await fetch('/api/create-envelope', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          output_name: outputName || 'output',
          private_key_content: privateKeyPath,
          public_key_content: publicKeyPath,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        addLog('error', data.error || 'Erro desconhecido ao criar o envelope.')
        return
      }

      data.steps?.forEach(step => addLog(step.status, step.message))
      addLog('success', `Envelope salvo em: ${data.output_folder}`)
      setSuccess(true)
    } catch (err) {
      addLog('error', `Erro de conexão com o servidor: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setForm(INITIAL_STATE)
    setLogs([])
    setSuccess(false)
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <h2 className="panel-title">CRIAR ENVELOPE</h2>
        <p className="panel-desc">
          Cifra a mensagem com AES-CBC, assina com RSA e encapsula a chave de sessão.
        </p>
      </div>

      <div className="form-grid">
        <div className="field full-width">
          <label className="field-label">
            <span className="field-num">01</span> MENSAGEM
            <span className="required">*</span>
          </label>
          <textarea
            className="field-input textarea"
            placeholder="Digite a mensagem a ser cifrada..."
            value={form.message}
            onChange={handleChange('message')}
            rows={4}
            disabled={loading}
          />
        </div>

        <div className="field">
          <label className="field-label">
            <span className="field-num">02</span> NOME DO ARQUIVO DE SAÍDA
          </label>
          <input
            className="field-input"
            type="text"
            placeholder="output (padrão)"
            value={form.outputName}
            onChange={handleChange('outputName')}
            disabled={loading}
          />
        </div>

        <div className="field" />

        <FileInput
          num="03"
          label="CHAVE PRIVADA (Remetente)"
          required
          value={form.privateKeyPath}
          onChange={handleChange('privateKeyPath')}
          disabled={loading}
          hint="Usada para assinar a mensagem"
        />

        <FileInput
          num="04"
          label="CHAVE PÚBLICA (Destinatário)"
          required
          value={form.publicKeyPath}
          onChange={handleChange('publicKeyPath')}
          disabled={loading}
          hint="Usada para cifrar a chave de sessão"
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
            <> CRIAR ENVELOPE</>
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
        <StatusLog logs={logs} success={success} />
      )}
    </div>
  )
}

export default CreateEnvelope
