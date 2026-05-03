import { useRef } from 'react'

function FileInput({ num, label, required, value, onChange, disabled, hint }) {
  const inputRef = useRef(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (evt) => {
      onChange({ target: { value: evt.target.result } })
    }
    reader.readAsText(file)
  }

  // Extrai o tipo da chave da primeira linha do PEM para exibição
  const fileType = value
    ? value.split('\n')[0].replace('-----BEGIN ', '').replace('-----', '').trim()
    : null

  return (
    <div className="field">
      <label className="field-label">
        <span className="field-num">{num}</span> {label}
        {required && <span className="required">*</span>}
      </label>

      <input
        ref={inputRef}
        type="file"
        accept=".pem,.key,.crt"
        style={{ display: 'none' }}
        onChange={handleFileChange}
        disabled={disabled}
      />

      <button
        type="button"
        className={`file-picker-btn ${value ? 'has-file' : ''} ${disabled ? 'is-disabled' : ''}`}
        onClick={() => !disabled && inputRef.current?.click()}
      >
        <span className="file-picker-icon">{value ? '✓' : '↑'}</span>
        <span className="file-picker-text">
          {fileType
            ? <><span className="file-type">{fileType}</span><span className="file-loaded"> · carregado</span></>
            : 'Selecionar arquivo .pem'
          }
        </span>
        {value && (
          <span
            role="button"
            className="file-clear-btn"
            onClick={(e) => {
              e.stopPropagation()
              onChange({ target: { value: '' } })
              if (inputRef.current) inputRef.current.value = ''
            }}
          >
            ✕
          </span>
        )}
      </button>

      {hint && <span className="field-hint">{hint}</span>}
    </div>
  )
}

export default FileInput
