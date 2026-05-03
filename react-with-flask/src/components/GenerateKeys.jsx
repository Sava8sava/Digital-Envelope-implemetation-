import { useState } from 'react'
import StatusLog from './StatusLog'

const KEY_SIZES = [
  { value: 2048, label: '2048 bits', recommended: true },
  { value: 1024, label: '1024 bits', recommended: false },
]

const INITIAL_STATE = {
  keySize: 2048,
  identity: '',
}

function GenerateKeys() {
  const [form, setForm]       = useState(INITIAL_STATE)
  const [logs, setLogs]       = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)

  const addLog = (status, message) => {
    setLogs(prev => [...prev, { status, message, id: Date.now() + Math.random() }])
  }

  const handleSubmit = async () => {
    setLogs([])
    setResult(null)
    setLoading(true)

    try {
      addLog('info', 'Iniciando geração do par de chaves RSA...')

      const response = await fetch('/api/generate-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          key_size: form.keySize,
          identity: form.identity.trim() || null,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        addLog('error', data.error || 'Erro desconhecido ao gerar as chaves.')
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
        <h2 className="panel-title">GERAR CHAVES RSA</h2>
        <p className="panel-desc">
          Gera um par de chaves assimétricas (pública e privada) no formato PEM.
          Os arquivos são salvos no servidor com nome e timestamp únicos.
        </p>
      </div>

      <div className="form-grid">

        {/* Tamanho da chave */}
        <div className="field">
          <label className="field-label">
            <span className="field-num">01</span> TAMANHO DA CHAVE
            <span className="required">*</span>
          </label>
          <div className="key-size-group">
            {KEY_SIZES.map(opt => (
              <button
                key={opt.value}
                type="button"
                className={`key-size-btn ${form.keySize === opt.value ? 'active' : ''} ${loading ? 'is-disabled' : ''}`}
                onClick={() => !loading && setForm(f => ({ ...f, keySize: opt.value }))}
              >
                <span className="key-size-value">{opt.label}</span>
                {opt.recommended && (
                  <span className="key-size-tag">recomendado</span>
                )}
              </button>
            ))}
          </div>
          <span className="field-hint">
            2048 bits oferece segurança adequada para uso atual. 1024 bits é legado.
          </span>
        </div>

        {/* Identidade (opcional) */}
        <div className="field">
          <label className="field-label">
            <span className="field-num">02</span> IDENTIFICADOR <span className="field-optional">(opcional)</span>
          </label>
          <input
            className="field-input"
            type="text"
            placeholder="ex: alice, servidor-prod, grupo-a"
            value={form.identity}
            onChange={e => setForm(f => ({ ...f, identity: e.target.value }))}
            disabled={loading}
            maxLength={48}
          />
          <span className="field-hint">
            Usado como prefixo no nome do arquivo. Facilita identificar a quem a chave pertence.
          </span>
        </div>

      </div>

      <div className="action-row">
        <button
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading
            ? <><span className="spinner" /> GERANDO...</>
            : <>⚿ GERAR PAR DE CHAVES</>
          }
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
        <div className="keygen-result">
          <div className="keygen-result-header">
            <span className="result-label">CHAVES GERADAS</span>
            <span className="keygen-badge">✓ PAR RSA-{result.key_size}</span>
          </div>

          <div className="keygen-files">
            <KeyFileCard
              type="PRIVADA"
              filename={result.private_key_file}
              path={result.private_key_path}
              warning
            />
            <KeyFileCard
              type="PÚBLICA"
              filename={result.public_key_file}
              path={result.public_key_path}
            />
          </div>

          <div className="keygen-warning">
            <span className="keygen-warning-icon">⚠</span>
            <p>
              Guarde a <strong>chave privada</strong> em local seguro e nunca a compartilhe.
              Ela é usada para assinar mensagens e não pode ser recuperada se perdida.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

function KeyFileCard({ type, filename, path, warning }) {
  return (
    <div className={`key-file-card ${warning ? 'is-private' : 'is-public'}`}>
      <div className="key-file-type">
        {warning ? '🔒' : '🔓'} CHAVE {type}
      </div>
      <div className="key-file-name">{filename}</div>
      <div className="key-file-path">{path}</div>
    </div>
  )
}

export default GenerateKeys
