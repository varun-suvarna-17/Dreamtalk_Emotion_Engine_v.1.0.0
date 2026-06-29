import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { Button, Input, Card, Slider, Navbar } from '../components/ui';

export default function CreateTwin() {
  const router = useRouter();
  const [config, setConfig] = useState({
    name: '',
    profession: '',
    relationship: 'Friend',
    traits: { extroversion: 0.5, agreeableness: 0.5, neuroticism: 0.5, openness: 0.5, conscientiousness: 0.5 }
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    // Simulate API call to initialize twin
    setTimeout(() => {
      // Encode config into URL just for demo purposes
      const query = new URLSearchParams({ name: config.name, profession: config.profession }).toString();
      router.push(`/chat?${query}`);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-subtle relative overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute top-[20%] right-[-10%] w-[40%] h-[40%] bg-blue-200/40 blur-[100px] rounded-full animate-float"></div>
      <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/20 blur-[120px] rounded-full animate-float" style={{ animationDelay: '3s' }}></div>

      <Navbar moduleName="Twin Creation" />

      <main className="max-w-5xl mx-auto px-6 py-16 relative z-10">
        <div className="mb-10 animate-slide-up">
          <h1 className="text-4xl font-extrabold text-charcoal">Design Your Companion</h1>
          <p className="text-gray-500 mt-2 text-lg">Define their identity and shape their cognitive traits.</p>
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <div className="space-y-8 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <Card title="Basic Details" className="h-full">
              <div className="space-y-6 mt-4">
                <Input 
                  label="Name" 
                  value={config.name} 
                  onChange={(e) => setConfig({...config, name: e.target.value})} 
                  placeholder="e.g. Alex" 
                  required
                />
                <Input 
                  label="Profession" 
                  value={config.profession} 
                  onChange={(e) => setConfig({...config, profession: e.target.value})} 
                  placeholder="e.g. Software Architect" 
                  required
                />
                <div className="space-y-2 text-left">
                  <label className="text-sm font-medium text-charcoal ml-2">Relationship</label>
                  <div className="relative">
                    <select 
                      value={config.relationship} 
                      onChange={(e) => setConfig({...config, relationship: e.target.value})} 
                      className="w-full px-6 py-3 rounded-full border border-gray-200 bg-white/80 backdrop-blur-sm focus:outline-none focus:border-primary focus:ring-4 focus:ring-secondary/50 transition-all text-charcoal shadow-sm hover:shadow-md appearance-none"
                    >
                      <option value="Friend">Friend</option>
                      <option value="Partner">Partner</option>
                      <option value="Mentor">Mentor</option>
                      <option value="Colleague">Colleague</option>
                    </select>
                    <div className="absolute inset-y-0 right-6 flex items-center pointer-events-none">
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                    </div>
                  </div>
                </div>

                <div className="pt-4">
                  <label className="text-sm font-medium text-charcoal ml-2 mb-2 block">Visual Avatar</label>
                  <div className="border-2 border-dashed border-primary/30 bg-primary/5 hover:bg-primary/10 transition-colors rounded-3xl p-8 flex flex-col items-center justify-center text-center cursor-pointer">
                    <div className="w-16 h-16 bg-white rounded-full shadow-sm flex items-center justify-center mb-4">
                      <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                    </div>
                    <span className="text-sm font-medium text-primary">Upload Photo or Video</span>
                    <span className="text-xs text-gray-400 mt-1">Supports JPG, PNG, MP4</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          <div className="space-y-8 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <Card title="Cognitive Profiling" subtitle="Configure Big Five Personality Traits" className="h-full">
              <div className="space-y-8 mt-6">
                {Object.entries(config.traits).map(([trait, val]) => (
                  <Slider 
                    key={trait} 
                    label={trait.charAt(0).toUpperCase() + trait.slice(1)} 
                    value={val} 
                    onChange={(newVal) => setConfig({...config, traits: {...config.traits, [trait]: newVal}})} 
                  />
                ))}
              </div>
              
              <div className="mt-12 pt-6 border-t border-gray-100">
                <Button type="submit" loading={loading} className="w-full text-lg py-4">
                  Initialize Brain Module
                </Button>
              </div>
            </Card>
          </div>
        </form>
      </main>
    </div>
  );
}
