function StatusLog({ logs, success }) {
  const icons = {
    info: '·',
    success: '✓',
    error: '✗',
    warning: '!',
  }

  return (
    <div className="log-box">
      <div className="log-header">
        <span className="log-title">LOG DE OPERAÇÕES</span>
        <span className={`log-status ${success ? 'ok' : 'fail'}`}>
          {success ? 'CONCLUÍDO' : 'ERRO'}
        </span>
      </div>
      <ul className="log-list">
        {logs.map(log => (
          <li key={log.id} className={`log-entry log-${log.status}`}>
            <span className="log-icon">{icons[log.status] ?? '·'}</span>
            <span className="log-msg">{log.message}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default StatusLog
