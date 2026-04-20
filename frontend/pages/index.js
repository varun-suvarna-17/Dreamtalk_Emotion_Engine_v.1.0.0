import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Button, Input, Card, Slider, Navbar } from '../components/ui';

// Debounce utility function
const debounce = (func, delay) => {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
};

const BrainModuleChat = () => {
  // State for Personality Configuration
  const [config, setConfig] = useState({
    name: 'Alex',
    profession: 'Software Architect',
    relationship: 'Friend',
    tone: 'casual',
    traits: { extroversion: 0.6, agreeableness: 0.7, neuroticism: 0.3, openness: 0.9, conscientiousness: 0.8 }
  });
  const [isConfigured, setIsConfigured] = useState(false);

  // State for Chat
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [emotion, setEmotion] = useState({ display_name: 'Neutral', intensity: 'low', pad: [0, 0, 0] });
  const [error, setError] = useState(null);
  
  const chatEndRef = useRef(null);

  // Clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleStartChat = async () => {
    setLoading(true);
    setError(null);
    try {
      await axios.post('http://localhost:8000/configure', config);
      setIsConfigured(true);
      setMessages([{ 
        role: 'assistant', 
        text: `Hey! I'm ${config.name}. Ready to chat?`, 
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        emotion: 'Neutral'
      }]);
    } catch (err) {
      console.error("Config Error:", err);
      setError("Failed to initialize personality. Please check if the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const currentInput = input;
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg = { role: 'user', text: currentInput, timestamp };
    
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/chat', { user_input: currentInput });
      const assistantMsg = {
        role: 'assistant',
        text: response.data.response,
        emotion: response.data.emotion.display_name,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, assistantMsg]);
      setEmotion(response.data.emotion);
    } catch (err) {
      console.error("Chat Error:", err);
      setError("Failed to send message. Please try again.");
      // Optional: remove the user message that failed
      setMessages(prev => prev.filter(m => m !== userMsg));
      setInput(currentInput); // Put the text back
    } finally {
      setLoading(false);
    }
  };

  const updateTraitsLive = useCallback(
    debounce(async (trait, val) => {
      const newTraits = { ...config.traits, [trait]: val };
      const newConfig = { ...config, traits: newTraits };
      setConfig(newConfig);
      try {
        await axios.post('http://localhost:8000/configure', newConfig);
      } catch (err) {
        console.error("Live Trait Update Error:", err);
      }
    }, 500), // 500ms debounce delay
    [config]
  );

  if (!isConfigured) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
        <Navbar moduleName="Brain Module" />
        <main className="flex-1 flex items-center justify-center p-6 relative">
          {error && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-error text-white px-6 py-3 rounded-xl shadow-xl z-50 animate-slide-in-top flex items-center gap-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span className="text-sm font-bold">{error}</span>
            </div>
          )}
          <Card 
            title="Initialize Persona" 
            subtitle="Define the identity and cognitive traits of your digital human."
            className="w-full max-w-xl"
            footer={
              <Button onClick={handleStartChat} loading={loading} className="w-full">
                Initialize Brain Module
              </Button>
            }
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <Input label="Name" value={config.name} onChange={(e) => setConfig({...config, name: e.target.value})} placeholder="e.g. Alex" />
                <Input label="Profession" value={config.profession} onChange={(e) => setConfig({...config, profession: e.target.value})} placeholder="e.g. Software Architect" />
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Relationship</label>
                  <select 
                    value={config.relationship} 
                    onChange={(e) => setConfig({...config, relationship: e.target.value})} 
                    className="w-full px-4 py-2 rounded-lg border border-gray-200 bg-white focus:outline-none focus:border-primary transition-all text-sm text-gray-700"
                  >
                    <option value="Friend">Friend</option>
                    <option value="Partner">Partner</option>
                    <option value="Mentor">Mentor</option>
                    <option value="Colleague">Colleague</option>
                  </select>
                </div>
              </div>
              <div className="space-y-4 border-l border-gray-100 pl-6">
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Cognitive Profiling (Big Five)</h3>
                {Object.entries(config.traits).map(([trait, val]) => (
                  <Slider key={trait} label={trait} value={val} onChange={(newVal) => setConfig({...config, traits: {...config.traits, [trait]: newVal}})} />
                ))}
              </div>
            </div>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50 font-sans overflow-hidden relative">
      <Navbar moduleName="Active Session" />
      
      {error && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 bg-error text-white px-6 py-3 rounded-xl shadow-xl z-50 animate-slide-in-top flex items-center gap-3">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <span className="text-sm font-bold">{error}</span>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden max-w-[1200px] mx-auto w-full px-8 py-6 gap-8">
        {/* Sidebar: Cognitive Status */}
        <aside className="w-80 flex flex-col gap-6 hidden lg:flex">
          <Card title="Brain State" subtitle="Real-time neural and emotional diagnostics.">
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-blue-50 border border-blue-100 space-y-2">
                <label className="text-[10px] font-black text-primary uppercase tracking-tighter">Current Mood</label>
                <div className="flex items-center justify-between">
                  <span className="text-xl font-black text-gray-900 leading-none">{emotion.display_name}</span>
                  <span className="px-2 py-0.5 rounded-full bg-white text-[10px] font-bold text-primary border border-blue-100 uppercase">{emotion.intensity}</span>
                </div>
              </div>
              
              <div className="space-y-4">
                <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Active Traits</h4>
                {Object.entries(config.traits).map(([trait, val]) => (
                  <Slider 
                    key={trait} 
                    label={trait} 
                    value={val} 
                    onChange={(newVal) => updateTraitsLive(trait, newVal)} 
                  />
                ))}
              </div>
            </div>
          </Card>

          <Button variant="outline" onClick={() => setIsConfigured(false)} className="mt-auto">
            Reset Module
          </Button>
        </aside>

        {/* Main Chat Interface */}
        <main className="flex-1 flex flex-col">
          <Card className="flex-1 flex flex-col p-0 overflow-hidden" title={config.name} subtitle={config.profession}>
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-in-bottom`}>
                  <div className={`max-w-[80%] space-y-1`}>
                    <div className={`px-5 py-3 rounded-2xl shadow-sm text-sm leading-relaxed ${
                      msg.role === 'user' 
                        ? 'bg-primary text-white rounded-tr-none' 
                        : 'bg-gray-100 text-gray-800 rounded-tl-none border border-gray-200'
                    }`}>
                      {msg.emotion && (
                        <div className="text-[8px] font-black uppercase tracking-[0.2em] mb-1 opacity-60">
                          {msg.emotion}
                        </div>
                      )}
                      {msg.text}
                    </div>
                    <div className={`text-[9px] font-bold text-gray-400 uppercase ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                      {msg.timestamp}
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-50 border border-gray-100 px-5 py-3 rounded-2xl rounded-tl-none flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce"></div>
                    </div>
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Neural Processing</span>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input Container */}
            <div className="p-6 bg-gray-50 border-t border-gray-100 flex items-center gap-4">
              <input 
                type="text" 
                value={input} 
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder={`Send a message to ${config.name}...`}
                className="flex-1 bg-white border border-gray-200 rounded-xl px-5 py-3 text-sm focus:outline-none focus:border-primary focus:ring-4 focus:ring-blue-50/50 transition-all shadow-sm"
              />
              <Button onClick={handleSendMessage} loading={loading} className="h-[46px] w-[46px] !p-0 rounded-xl shadow-lg">
                <svg viewBox="0 0 24 24" className="w-5 h-5 fill-white rotate-45 -translate-y-0.5"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
              </Button>
            </div>
          </Card>
        </main>
      </div>
    </div>
  );
};

export default BrainModuleChat;
