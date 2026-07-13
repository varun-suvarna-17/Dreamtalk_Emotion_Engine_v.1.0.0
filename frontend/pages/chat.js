import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { Button, Card, Navbar } from '../components/ui';

export default function ChatInterface() {
  const router = useRouter();
  const { name = 'Alex', profession = 'Assistant' } = router.query;
  
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', text: `Hi! I'm ${name}, your new ${profession}. How can I help you today?`, time: '10:00 AM', emotion: 'Joyful' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [emotionState, setEmotionState] = useState({ name: 'Joyful', pad: [0.8, 0.5, 0.2] });
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userInput = input.trim();
    const userMsg = {
      id: Date.now(),
      role: 'user',
      text: userInput,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const activeSessionId = sessionId || `web-${Date.now()}`;

    try {
      const response = await fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput,
          session_id: activeSessionId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Chat request failed with ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      const emotion = data.emotion || {};
      const pad = Array.isArray(emotion.pad) ? emotion.pad : emotionState.pad;
      const displayName = emotion.display_name || emotion.name || emotionState.name;

      setSessionId(data.session_id || activeSessionId);
      setEmotionState({ name: displayName, pad });
      setMessages(prev => [...prev, {
        id: Date.now(),
        role: 'assistant',
        text: data.response,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        emotion: displayName
      }]);
    } catch (error) {
      console.error('Failed to send chat message:', error);
      setMessages(prev => [...prev, {
        id: Date.now(),
        role: 'assistant',
        text: 'Sorry, I could not reach the brain backend. Please check the console and make sure the Python service is running on port 8000.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        emotion: 'Connection Error'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-subtle overflow-hidden relative">
      {/* Background Ambience based on emotion */}
      <div 
        className="absolute inset-0 opacity-20 mix-blend-multiply transition-colors duration-1000"
        style={{ 
          backgroundColor: emotionState.pad[0] > 0.5 ? '#60A5FA' : (emotionState.pad[0] < 0.2 ? '#94A3B8' : '#A78BFA') 
        }}
      />
      
      <Navbar moduleName="Active Session" />

      <div className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8 grid grid-cols-1 lg:grid-cols-4 gap-8 relative z-10 h-[calc(100vh-80px)]">
        
        {/* Avatar & Emotion Panel */}
        <div className="hidden lg:flex flex-col gap-6 col-span-1">
          <Card className="flex flex-col items-center text-center !px-6 !py-10">
            {/* Floating Avatar Container */}
            <div className="relative w-40 h-40 mb-6">
              <div className="absolute inset-0 bg-primary/20 rounded-full blur-xl animate-pulse"></div>
              <div className="relative w-full h-full rounded-full border-4 border-white shadow-floating overflow-hidden bg-white animate-float flex items-center justify-center">
                {/* Fallback avatar visual */}
                <svg className="w-20 h-20 text-primary/50" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
              </div>
            </div>
            
            <h2 className="text-2xl font-bold text-charcoal">{name}</h2>
            <p className="text-sm text-primary font-semibold">{profession}</p>

            {/* PAD Emotion Indicator */}
            <div className="w-full mt-10 space-y-4 text-left bg-gray-50/50 p-4 rounded-2xl border border-gray-100">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Current State</span>
                <span className="text-sm font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-md">{emotionState.name}</span>
              </div>
              
              {[
                { label: 'Pleasure', val: emotionState.pad[0], color: 'bg-green-400' },
                { label: 'Arousal', val: emotionState.pad[1], color: 'bg-orange-400' },
                { label: 'Dominance', val: emotionState.pad[2], color: 'bg-purple-400' }
              ].map((dim, i) => (
                <div key={i} className="space-y-1">
                  <div className="flex justify-between text-[10px] font-semibold text-gray-500 uppercase">
                    <span>{dim.label}</span>
                    <span>{(dim.val * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${dim.color} transition-all duration-1000 ease-out`} 
                      style={{ width: `${Math.max(0, Math.min(100, dim.val * 100))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Chat Interface */}
        <div className="glass col-span-1 lg:col-span-3 h-full flex flex-col rounded-[2rem] shadow-floating transition-all duration-300 overflow-hidden">
          {/* Mobile Header (visible only on small screens) */}
          <div className="lg:hidden bg-white border-b border-gray-100 p-4 flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-primary" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
            </div>
            <div>
              <h2 className="font-bold text-charcoal">{name}</h2>
              <p className="text-xs text-primary">{emotionState.name}</p>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50/30">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}>
                <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} max-w-[75%]`}>
                  {msg.role === 'assistant' && msg.emotion && (
                    <span className="text-[10px] font-bold text-gray-400 uppercase mb-1 ml-2 tracking-wider">
                      {msg.emotion}
                    </span>
                  )}
                  <div 
                    className={`px-6 py-3.5 shadow-sm text-[15px] leading-relaxed relative ${
                      msg.role === 'user' 
                        ? 'bg-primary text-white rounded-2xl rounded-tr-sm' 
                        : 'bg-white text-charcoal border border-gray-100 rounded-2xl rounded-tl-sm'
                    }`}
                  >
                    {/* Tail for WhatsApp style bubble */}
                    <div className={`absolute top-0 w-4 h-4 ${
                      msg.role === 'user' 
                        ? 'bg-primary -right-1.5' 
                        : 'bg-white border-t border-l border-gray-100 -left-1.5'
                    }`} style={{ clipPath: msg.role === 'user' ? 'polygon(0 0, 100% 0, 0 100%)' : 'polygon(0 0, 100% 0, 100% 100%)' }} />
                    
                    <span className="relative z-10 block">{msg.text}</span>
                  </div>
                  <span className={`text-[10px] text-gray-400 mt-1 font-medium ${msg.role === 'user' ? 'mr-1' : 'ml-1'}`}>
                    {msg.time}
                  </span>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start animate-fade-in">
                <div className="bg-white border border-gray-100 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-2">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 bg-white border-t border-gray-100">
            <form onSubmit={handleSend} className="flex items-center gap-3 bg-gray-50 p-2 rounded-full border border-gray-200 focus-within:ring-4 focus-within:ring-primary/10 focus-within:border-primary/30 transition-all">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 bg-transparent border-none focus:outline-none px-4 text-charcoal placeholder:text-gray-400"
              />
              <Button type="submit" loading={loading} className="!w-12 !h-12 !p-0 rounded-full shadow-md flex-shrink-0">
                <svg viewBox="0 0 24 24" className="w-5 h-5 fill-white rotate-45 -translate-y-0.5 -translate-x-0.5"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
