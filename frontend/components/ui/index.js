import React from 'react';
import Link from 'next/link';

export const Button = ({ children, onClick, variant = 'primary', loading = false, className = '', href, ...props }) => {
  const baseStyles = "px-6 py-3 rounded-full font-medium transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 hover:-translate-y-1";
  
  const variants = {
    primary: "bg-primary text-white hover:bg-blue-500 shadow-floating hover:shadow-floating-hover",
    secondary: "bg-secondary text-charcoal hover:bg-blue-300 shadow-floating hover:shadow-floating-hover",
    outline: "border-2 border-primary text-primary hover:bg-subtle",
    danger: "bg-error text-white hover:bg-red-500 shadow-floating hover:shadow-floating-hover",
  };

  const Component = href ? Link : 'button';

  return (
    <Component 
      href={href}
      onClick={onClick} 
      className={`${baseStyles} ${variants[variant]} ${className}`}
      disabled={loading}
      {...props}
    >
      {loading ? (
        <svg className="animate-spin h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      ) : children}
    </Component>
  );
};

export const Input = ({ label, error, className = '', ...props }) => {
  return (
    <div className="w-full space-y-2 text-left">
      {label && <label className="text-sm font-medium text-charcoal ml-2">{label}</label>}
      <input 
        className={`w-full px-6 py-3 rounded-full border border-gray-200 bg-white/80 backdrop-blur-sm focus:outline-none focus:border-primary focus:ring-4 focus:ring-secondary/50 transition-all placeholder:text-gray-400 text-charcoal shadow-sm hover:shadow-md ${error ? 'border-error ring-red-100' : ''} ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-error font-medium ml-2">{error}</p>}
    </div>
  );
};

export const Card = ({ children, title, subtitle, className = '', footer }) => {
  return (
    <div className={`glass rounded-[2rem] shadow-floating hover:shadow-floating-hover transition-all duration-300 overflow-hidden flex flex-col ${className}`}>
      {(title || subtitle) && (
        <div className="px-8 py-6 border-b border-white/20">
          {title && <h3 className="text-2xl font-semibold text-charcoal">{title}</h3>}
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
      )}
      <div className="p-8 flex-1">{children}</div>
      {footer && <div className="px-8 py-6 border-t border-white/20">{footer}</div>}
    </div>
  );
};

export const Slider = ({ label, value, onChange, min = 0, max = 1, step = 0.1 }) => {
  return (
    <div className="w-full space-y-3">
      <div className="flex justify-between items-center ml-2 mr-2">
        <label className="text-sm font-medium text-charcoal">{label}</label>
        <span className="text-xs font-bold text-primary bg-subtle px-3 py-1 rounded-full">{value.toFixed(1)}</span>
      </div>
      <input 
        type="range" 
        min={min} 
        max={max} 
        step={step} 
        value={value} 
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-full appearance-none cursor-pointer accent-primary hover:accent-blue-400 transition-all shadow-inner"
      />
    </div>
  );
};

export const Navbar = ({ moduleName }) => {
  return (
    <nav className="h-20 bg-white/60 backdrop-blur-lg border-b border-white/40 px-10 flex items-center justify-between sticky top-0 z-50 shadow-sm transition-all">
      <Link href="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
        <div className="bg-gradient-to-tr from-primary to-secondary p-2.5 rounded-2xl shadow-md">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-charcoal tracking-tight">DreamTalk</h1>
          {moduleName && <p className="text-[11px] text-primary font-semibold uppercase tracking-widest leading-none mt-0.5">{moduleName}</p>}
        </div>
      </Link>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 bg-white/80 px-4 py-2 rounded-full shadow-sm border border-white/50">
          <div className="w-2.5 h-2.5 bg-success rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]"></div>
          <span className="text-xs font-semibold text-charcoal uppercase tracking-wider">System Online</span>
        </div>
      </div>
    </nav>
  );
};
