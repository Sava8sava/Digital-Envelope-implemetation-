import { useState, useRef } from 'react'
import StatusLog from './StatusLog'
import FileInput from './FileInput'

const ENVELOPE_FILES = ['mensagem.cif', 'signature.sig', 'session_key.env']

const INITIAL_STATE = {
  envelopeFiles: {},   // { filename -> File object }
  privateKeyContent: '',
  senderPublicKeyContent: '',
}

function OpenEnvelope() {
  const [form, setForm]       = useState(INITIAL_STATE)
  const [logs, setLogs]       = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const folderRef             = useRef(null)

  const addLog = (status, message) => {
    setLogs(prev => [...prev, { status, message, id: Date.now() + Math.random() }])
  }

  // Recebe a seleção de pasta e mapeia os arquivos esperados
  const handleFolderChange = (e) => {
    const files = Array.from(e.target.files)
    const mapped = {}
    files.forEach(file => {
      const name = file.name
      if (ENVELOPE_FILES.includes(name)) mapped[name] = file
    })
    setForm(prev => ({ ...prev, envelopeFiles: mapped }))
  }

  const clearFolder = () => {
    setForm(prev => ({ ...prev, envelopeFiles: {} }))
    if (folderRef.current) folderRef.current.value = ''
  }

  const foundFiles  = Object.keys(form.envelopeFiles)
  const missingFiles = ENVELOPE_FILES.filter(f => !form.envelopeFiles[f])
  const folderReady  = missingFiles.length === 0

  // Lê um File como ArrayBuffer e retorna base64
  const readAsBase64 = (file) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload  = () => {
        const bytes  = new Uint8Array(reader.result)
        const binary = bytes.reduce((acc, b) => acc + String.fromCharCode(b), '')
        resolve(btoa(binary))
      }
      reader.onerror = reject
      reader.readAsArrayBuffer(file)
    })

  const handleSubmit = async () => {
    const { envelopeFiles, privateKeyContent, senderPublicKeyContent } = form

    if (!folderReady) {
      addLog('error', `Erro: pasta incompleta. Faltam: ${missingFiles.join(', ')}`)
      return
    }
    if (!privateKeyContent || !senderPublicKeyContent) {
      addLog('error', 'Erro: selecione ambas as chaves.')
      return
    }

    setLogs([])
    setLoading(true)
    setResult(null)

    try {
      addLog('info', 'Lendo arquivos do envelope...')

      // Lê os três arquivos binários como base64
      const [cipherB64, sigB64, keyB64] = await Promise.all([
        readAsBase64(envelopeFiles['mensagem.cif']),
        readAsBase64(envelopeFiles['signature.sig']),
        readAsBase64(envelopeFiles['session_key.env']),
      ])

      addLog('info', 'Iniciando processo de abertura do envelope...')

      const response = await fetch('/api/open-envelope', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ciphertext_b64:        cipherB64,
          signature_b64:         sigB64,
          session_key_b64:       keyB64,
          private_key_content:   privateKeyContent,
          sender_public_key_content: senderPublicKeyContent,
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
      addLog('error', `Erro: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setForm(INITIAL_STATE)
    setLogs([])
    setResult(null)
    if (folderRef.current) folderRef.current.value = ''
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <h2 className="panel-title">ABRIR ENVELOPE</h2>
        <p className="panel-desc">
          Decifra a chave de sessão com RSA, recupera a mensagem via AES-CBC
          e valida a assinatura digital.
        </p>
      </div>

      <div className="form-grid">

        {/* Seleção da pasta do envelope */}
        <div className="field full-width">
          <label className="field-label">
            <span className="field-num">01</span> PASTA DO ENVELOPE
            <span className="required">*</span>
          </label>

          {/* Input oculto com webkitdirectory */}
          <input
            ref={folderRef}
            type="file"
            webkitdirectory="true"
            multiple
            style={{ display: 'none' }}
            onChange={handleFolderChange}
            disabled={loading}
          />

          <button
            type="button"
            className={`file-picker-btn ${folderReady ? 'has-file' : ''} ${loading ? 'is-disabled' : ''}`}
            onClick={() => !loading && folderRef.current?.click()}
          >
            <span className="file-picker-icon">{folderReady ? '✓' : '↑'}</span>
            <span className="file-picker-text">
              {foundFiles.length === 0
                ? 'Selecionar pasta do envelope'
                : folderReady
                  ? <><span className="file-type">Pasta selecionada</span><span className="file-loaded"> · {foundFiles.length} arquivos encontrados</span></>
                  : <><span className="file-type" style={{color:'var(--yellow)'}}>Pasta incompleta</span><span className="file-loaded"> · {foundFiles.length}/3 arquivos</span></>
              }
            </span>
            {foundFiles.length > 0 && (
              <span
                role="button"
                className="file-clear-btn"
                onClick={(e) => { e.stopPropagation(); clearFolder() }}
              >
                ✕
              </span>
            )}
          </button>

          {/* Checklist dos arquivos esperados */}
          <div className="envelope-checklist">
            {ENVELOPE_FILES.map(name => {
              const found = !!form.envelopeFiles[name]
              return (
                <span key={name} className={`checklist-item ${found ? 'found' : 'missing'}`}>
                  {found ? '✓' : '○'} {name}
                </span>
              )
            })}
          </div>
        </div>

        <FileInput
          num="02"
          label="CHAVE PRIVADA (Destinatário)"
          required
          value={form.privateKeyContent}
          onChange={e => setForm(prev => ({ ...prev, privateKeyContent: e.target.value }))}
          disabled={loading}
          hint="Usada para decifrar a chave de sessão"
        />

        <FileInput
          num="03"
          label="CHAVE PÚBLICA (Remetente)"
          required
          value={form.senderPublicKeyContent}
          onChange={e => setForm(prev => ({ ...prev, senderPublicKeyContent: e.target.value }))}
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
          {loading
            ? <><span className="spinner" /> PROCESSANDO...</>
            : <> ABRIR ENVELOPE</>
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
