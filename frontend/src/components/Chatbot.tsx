import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, Bot, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://127.0.0.1:8002';

interface Message {
  text: string;
  type: 'user' | 'bot';
}

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Chatbot = () => {
  const [messages, setMessages] = useState<Message[]>([
    { text: "Hello! I'm your **DentaFlow AI assistant**. How can I help you today?", type: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input;
    setMessages(prev => [...prev, { text: userMsg, type: 'user' }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          question: userMsg,
          conversation_id: conversationId 
        })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { text: data.answer, type: 'bot' }]);
        if (data.conversation_id) {
          setConversationId(data.conversation_id);
        }
      } else {
        setMessages(prev => [...prev, { text: "I'm having trouble connecting to the AI service. Please try again later.", type: 'bot' }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { text: "Network error. Please check your connection.", type: 'bot' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages" ref={scrollRef}>
        <AnimatePresence initial={false}>
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.2 }}
              className={`message ${m.type}`}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{ 
                  marginTop: '0.25rem',
                  color: m.type === 'bot' ? 'var(--primary)' : 'rgba(255,255,255,0.7)',
                  flexShrink: 0
                }}>
                  {m.type === 'bot' ? <Bot size={20} /> : <User size={20} />}
                </div>
                <div className="markdown-content" style={{ fontSize: '0.95rem', lineHeight: '1.6' }}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {m.text}
                  </ReactMarkdown>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="message bot"
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
              <Loader2 className="loader-spin" size={16} />
              AI Assistant is thinking...
            </div>
          </motion.div>
        )}
      </div>

      <form className="chat-input-area" onSubmit={sendMessage}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask anything about your dental health..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit" className="btn-primary" style={{ width: 'auto', padding: '0.75rem 1.5rem' }}>
          <Send size={18} />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
};

export default Chatbot;
