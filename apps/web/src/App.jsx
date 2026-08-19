import React, { useState, useEffect } from 'react';

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [mode, setMode] = useState('friend');
  const [messages, setMessages] = useState([
    { sender: 'assistant', text: 'Hello! I am NEUROCORE. How can I assist you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState('Checking...');

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(res => res.json())
      .then(data => setServerStatus(`Online (v${data.version})`))
      .catch(() => setServerStatus('Disconnected'));
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, mode: mode })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { sender: 'assistant', text: data.response }]);
      } else {
        setMessages(prev => [...prev, { sender: 'assistant', text: `Error: ${res.statusText}` }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'assistant', text: `API Connection Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="logo">
          🧠 NEUROCORE
        </div>
        <div className="status-badge">
          ● API {serverStatus}
        </div>

        <div className="nav-section-title">Modes</div>
        <div className="mode-list">
          {['friend', 'plan', 'terminal', 'build', 'voice'].map(m => (
            <button
              key={m}
              className={`mode-btn ${mode === m ? 'active' : ''}`}
              onClick={() => setMode(m)}
            >
              {m.toUpperCase()}
            </button>
          ))}
        </div>
      </aside>

      <main className="main-content">
        <header className="header">
          <h2>Mode: <span style={{ color: 'var(--accent-cyan)' }}>{mode}</span></h2>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Core: Qwen3 8B (Local)
          </div>
        </header>

        <div className="messages-panel">
          {messages.map((msg, i) => (
            <div key={i} className={`message-card ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
          {loading && (
            <div className="message-card assistant" style={{ fontStyle: 'italic', opacity: 0.7 }}>
              NEUROCORE is thinking...
            </div>
          )}
        </div>

        <div className="input-area">
          <input
            type="text"
            className="chat-input"
            placeholder={`Message NEUROCORE in ${mode} mode...`}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
          />
          <button className="send-btn" onClick={handleSend} disabled={loading}>
            Send
          </button>
        </div>
      </main>
    </div>
  );
}
