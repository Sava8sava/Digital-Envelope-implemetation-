import { useState } from 'react'
import CreateEnvelope from './components/CreateEnvelope'
import OpenEnvelope from './components/OpenEnvelope'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('create')

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
        <button
          className={`tab-btn ${activeTab === 'create' ? 'active' : ''}`}
          onClick={() => setActiveTab('create')}
        >
          <span className="tab-num">01</span>
          CRIAR ENVELOPE
        </button>
        <button
          className={`tab-btn ${activeTab === 'open' ? 'active' : ''}`}
          onClick={() => setActiveTab('open')}
        >
          <span className="tab-num">02</span>
          ABRIR ENVELOPE
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'create' ? <CreateEnvelope /> : <OpenEnvelope />}
      </main>

      <footer className="app-footer">
        <span>RSA · AES-CBC · SHA-512</span>
        <span>PKCS#8 · PKCS1v15</span>
      </footer>
    </div>
  )
}

export default App
