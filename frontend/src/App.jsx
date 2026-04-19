import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Upload, 
  FileText, 
  Trash2, 
  MessageSquare, 
  Plus,
  Loader2,
  Trash
} from 'lucide-react';
import { documentService, chatService, sessionId } from './api';

const App = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const init = async () => {
      try {
        const [docs, history] = await Promise.all([
          documentService.list(),
          chatService.getHistory()
        ]);
        setDocuments(docs);
        setMessages(history);
      } catch (err) {
        console.error("Initialization failed", err);
      }
    };
    init();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    try {
      await documentService.upload(file);
      const docs = await documentService.list();
      setDocuments(docs);
    } catch (err) {
      alert("Upload failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMsg = { role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await chatService.query(query, selectedDocId);
      setMessages(prev => [...prev, response]);
    } catch (err) {
      const errMsg = { role: 'assistant', content: "Error: " + (err.response?.data?.detail || "Failed to reach server") };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteDoc = async (docId) => {
    try {
      await documentService.remove(docId);
      setDocuments(prev => prev.filter(d => d.doc_id !== docId));
    } catch (err) {
        console.error("Delete failed", err);
    }
  };

  const clearChat = async () => {
    if (window.confirm("Clear all chat history?")) {
        try {
            await chatService.clearHistory();
            setMessages([]);
        } catch (err) {
            console.error("Clear failed", err);
        }
    }
  };

  return (
    <div className="app-container">
      
      {/* Sidebar */}
      <aside className="sidebar">
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'rgba(99, 102, 241, 0.15)', padding: '0.5rem', borderRadius: '0.75rem', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
            <MessageSquare size={24} color="#818cf8" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', letterSpacing: '-0.025em', fontWeight: 700 }}>DocChat</h1>
            <p style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.1em', opacity: 0.5, fontWeight: 700 }}>AI Assistant</p>
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem', padding: '0 0.5rem' }}>
            <h2 style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-secondary)', fontWeight: 700 }}>Documents</h2>
            <span style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#818cf8', fontSize: '10px', padding: '2px 8px', borderRadius: '10px', fontWeight: 700 }}>
              {documents.length}
            </span>
          </div>
          
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="btn btn-secondary"
            style={{ width: '100%', marginBottom: '1rem', padding: '0.75rem' }}
          >
            {isUploading ? <Loader2 className="spinner" size={18} /> : <Plus size={18} />}
            Upload New
          </button>
          
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleUpload} 
            style={{ display: 'none' }} 
            accept=".pdf,.docx,.txt"
          />

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div 
              className={`doc-item ${!selectedDocId ? 'doc-item-active' : ''}`}
              onClick={() => setSelectedDocId(null)}
              style={{ cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.4rem', borderRadius: '0.5rem' }}>
                  <MessageSquare size={16} color={!selectedDocId ? "#818cf8" : "#94a3b8"} />
                </div>
                <span style={{ fontSize: '0.875rem' }}>All Documents</span>
              </div>
            </div>

            {documents.map(doc => (
              <div 
                key={doc.doc_id} 
                className={`doc-item group ${selectedDocId === doc.doc_id ? 'doc-item-active' : ''}`}
                onClick={() => setSelectedDocId(doc.doc_id)}
                style={{ cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', minWidth: 0 }}>
                  <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.4rem', borderRadius: '0.5rem' }}>
                    <FileText size={16} color={selectedDocId === doc.doc_id ? "#818cf8" : "#94a3b8"} />
                  </div>
                  <span style={{ fontSize: '0.875rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {doc.filename}
                  </span>
                </div>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteDoc(doc.doc_id);
                    if (selectedDocId === doc.doc_id) setSelectedDocId(null);
                  }}
                  style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', opacity: 0.4 }}
                  onMouseEnter={(e) => e.currentTarget.style.opacity = 1}
                  onMouseLeave={(e) => e.currentTarget.style.opacity = 0.4}
                >
                  <Trash2 size={14} color="#ef4444" />
                </button>
              </div>
            ))}
            {documents.length === 0 && (
              <div style={{ textAlign: 'center', padding: '2rem 0', opacity: 0.3, fontSize: '0.75rem' }}>
                No documents uploaded
              </div>
            )}
          </div>
        </div>

        <div style={{ padding: '1rem', borderTop: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0 0.5rem' }}>
                <span style={{ fontSize: '9px', textTransform: 'uppercase', opacity: 0.4, fontWeight: 700 }}>Session</span>
                <span style={{ fontSize: '9px', color: '#818cf8', fontWeight: 700 }}>{sessionId.slice(0, 8)}</span>
            </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        
        {/* Header */}
        <header style={{ height: '72px', borderBottom: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 2rem', background: 'rgba(15, 23, 42, 0.4)', backdropFilter: 'blur(8px)', zIndex: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px rgba(16, 185, 129, 0.5)' }}></div>
            <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)' }}>System Live</span>
          </div>
          {messages.length > 0 && (
            <button onClick={clearChat} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                Clear Chat <Trash size={12} />
            </button>
          )}
        </header>

        {/* Chat Thread */}
        <div className="chat-thread">
          {messages.length === 0 ? (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', maxWidth: '400px', margin: '0 auto', gap: '1.5rem' }}>
                <div style={{ width: '80px', height: '80px', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                    <MessageSquare size={32} color="#818cf8" />
                </div>
                <div>
                   <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Ready to Assist</h3>
                   <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                     Upload documents and ask questions. I'll provide answers based directly on your stored data.
                   </p>
                </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role === 'user' ? 'message-user' : 'message-ai'}`}>
                {msg.content}
              </div>
            ))
          )}
          {isLoading && (
            <div className="message message-ai" style={{ width: 'fit-content' }}>
              <div style={{ display: 'flex', gap: '4px' }}>
                <div className="spinner" style={{ width: '4px', height: '4px', background: '#818cf8', borderRadius: '50%' }}></div>
                <div className="spinner" style={{ width: '4px', height: '4px', background: '#818cf8', borderRadius: '50%', animationDelay: '0.2s' }}></div>
                <div className="spinner" style={{ width: '4px', height: '4px', background: '#818cf8', borderRadius: '50%', animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-container">
          <div style={{ maxWidth: '900px', margin: '0 auto 0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0 0.5rem' }}>
             <span style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', fontWeight: 600 }}>
               Targeting:
             </span>
             <span style={{ fontSize: '11px', color: '#818cf8', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
               {selectedDocId ? (
                 <>
                   <FileText size={12} />
                   {documents.find(d => d.doc_id === selectedDocId)?.filename || 'Selected Document'}
                 </>
               ) : (
                 <>
                   <MessageSquare size={12} />
                   All Uploaded Documents
                 </>
               )}
             </span>
          </div>
          <form onSubmit={handleSend} className="input-glass">
            <textarea 
               value={query}
               onChange={(e) => setQuery(e.target.value)}
               placeholder="Enter your question..."
               className="chat-textarea"
               onKeyDown={(e) => {
                 if (e.key === 'Enter' && !e.shiftKey) {
                   e.preventDefault();
                   handleSend(e);
                 }
               }}
            />
            <button 
              type="submit"
              disabled={!query.trim() || isLoading}
              className="btn btn-primary glow"
              style={{ borderRadius: '0.75rem', padding: '0.75rem' }}
            >
              {isLoading ? <Loader2 className="spinner" size={20} /> : <Send size={20} />}
            </button>
          </form>
          <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '9px', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-secondary)', fontWeight: 700 }}>
             Secure RAG Pipeline • Powered by Groq • Llama 3
          </div>
        </div>

        {/* Background Gradients */}
        <div style={{ position: 'absolute', top: '-10%', left: '-10%', width: '40%', height: '40%', background: 'rgba(99, 102, 241, 0.05)', borderRadius: '50%', filter: 'blur(100px)', pointerEvents: 'none' }}></div>
        <div style={{ position: 'absolute', bottom: '-10%', right: '-10%', width: '40%', height: '40%', background: 'rgba(139, 92, 246, 0.05)', borderRadius: '50%', filter: 'blur(100px)', pointerEvents: 'none' }}></div>
      </main>
    </div>
  );
};

export default App;
