import React from 'react';
import { Button, Card, Navbar } from '../components/ui';

export default function Home() {
  return (
    <div className="min-h-screen bg-subtle bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] overflow-hidden relative selection:bg-primary selection:text-white">
      {/* Background Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 blur-[120px] rounded-full mix-blend-multiply animate-float"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-secondary/30 blur-[150px] rounded-full mix-blend-multiply animate-float" style={{ animationDelay: '2s' }}></div>

      <Navbar moduleName="Welcome" />

      <main className="max-w-7xl mx-auto px-6 pt-24 pb-32 flex flex-col items-center text-center relative z-10">
        <div className="animate-slide-up space-y-6 max-w-4xl">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/50 border border-primary/20 text-primary text-sm font-semibold mb-4 backdrop-blur-sm shadow-sm">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary"></span>
            </span>
            DreamTalk v2.0 is Live
          </div>
          
          <h1 className="text-6xl md:text-8xl font-extrabold text-charcoal tracking-tight leading-tight">
            Create Your <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-400">
              Digital Twin
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-500 font-medium max-w-2xl mx-auto leading-relaxed">
            Craft highly intelligent, emotionally aware AI companions with our antigravity cognitive engine.
          </p>

          <div className="pt-8 flex flex-col sm:flex-row items-center justify-center gap-6">
            <Button href="/create" className="text-lg px-10 py-5 w-full sm:w-auto">
              Get Started Now
            </Button>
            <Button href="#" variant="secondary" className="text-lg px-10 py-5 w-full sm:w-auto">
              View Demo
            </Button>
          </div>
        </div>

        <div className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
          {[
            {
              title: "Emotional AI",
              desc: "Experience real-time PAD emotional state transitions."
            },
            {
              title: "Personality Config",
              desc: "Fine-tune behavior using Big Five trait sliders."
            },
            {
              title: "Seamless Chat",
              desc: "Engage in fluid, low-latency conversational interfaces."
            }
          ].map((feature, i) => (
            <div key={i} className="animate-slide-up" style={{ animationDelay: `${0.2 * (i+1)}s` }}>
              <Card className="h-full items-center text-center hover:-translate-y-2 !p-10">
                <div className="w-12 h-12 mb-6 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                  <div className="w-4 h-4 rounded-full bg-primary animate-pulse"></div>
                </div>
                <h3 className="text-2xl font-bold text-charcoal mb-3">{feature.title}</h3>
                <p className="text-gray-500 font-medium">{feature.desc}</p>
              </Card>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
