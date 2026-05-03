import { useState } from 'react'
import CreateEnvelope from './components/CreateEnvelope'
import OpenEnvelope from './components/OpenEnvelope'
import GenerateKeys from './components/GenerateKeys'
import './App.css'

const TABS = [
  { id: 'keys',   num: '01', label: 'GERAR CHAVES'   },
  { id: 'create', num: '02', label: 'CRIAR ENVELOPE' },
  { id: 'open',   num: '03', label: 'ABRIR ENVELOPE' },
]

function App() {
  const [activeTab, setActiveTab] = useState('keys')

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="logo-area">
            <span className="logo-icon">⬡</span>
            <div>
              <h1 className="app-title">ENVELOPE DIGITAL</h1>
              <p className="app-subtitle">Sistema de Criptografia Assimétrica · UFPI</p>
            </div>
          </div>
          <div className="status-badge">
            <span className="status-dot" />
            SISTEMA ATIVO
          </div>
        </div>
      </header>

      <nav className="tab-nav">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-num">{tab.num}</span>
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="main-content">
        {activeTab === 'keys'   && <GenerateKeys />}
        {activeTab === 'create' && <CreateEnvelope />}
        {activeTab === 'open'   && <OpenEnvelope />}
      </main>

      <footer className="app-footer">
        <span>RSA · AES-CBC · SHA-512</span>
        <span>PKCS#8 · PKCS1v15</span>
      </footer>
    </div>
  )
}

export default App
