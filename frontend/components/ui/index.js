import React from 'react';

export const Button = ({ children, onClick, variant = 'primary', loading = false, className = '', ...props }) => {
  const baseStyles = "px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95";
  
  const variants = {
    primary: "bg-primary text-white hover:bg-blue-700 shadow-md hover:shadow-lg",
    secondary: "bg-gray-100 text-gray-700 hover:bg-gray-200",
    outline: "border-2 border-primary text-primary hover:bg-blue-50",
    danger: "bg-error text-white hover:bg-red-600",
  };

  return (
    <button 
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
    </button>
  );
};

export const Input = ({ label, error, className = '', ...props }) => {
  return (
    <div className="w-full space-y-1">
      {label && <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{label}</label>}
      <input 
        className={`w-full px-4 py-2 rounded-lg border border-gray-200 bg-white focus:outline-none focus:border-primary focus:ring-2 focus:ring-blue-100 transition-all placeholder:text-gray-400 text-gray-700 ${error ? 'border-error ring-red-100' : ''} ${className}`}
        {...props}
      />
      {error && <p className="text-[10px] text-error font-medium">{error}</p>}
    </div>
  );
};

export const Card = ({ children, title, subtitle, className = '', footer }) => {
  return (
    <div className={`bg-white rounded-2xl border border-gray-100 shadow-soft overflow-hidden flex flex-col ${className}`}>
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-50 bg-gray-50/30">
          {title && <h3 className="text-lg font-bold text-gray-800">{title}</h3>}
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
      )}
      <div className="p-6 flex-1">{children}</div>
      {footer && <div className="px-6 py-4 border-t border-gray-50 bg-gray-50/30">{footer}</div>}
    </div>
  );
};

export const Slider = ({ label, value, onChange, min = 0, max = 1, step = 0.1 }) => {
  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{label}</label>
        <span className="text-xs font-bold text-primary bg-blue-50 px-2 py-0.5 rounded">{value.toFixed(1)}</span>
      </div>
      <input 
        type="range" 
        min={min} 
        max={max} 
        step={step} 
        value={value} 
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 bg-gray-100 rounded-lg appearance-none cursor-pointer accent-primary hover:accent-blue-700 transition-all"
      />
    </div>
  );
};

export const Navbar = ({ moduleName }) => {
  return (
    <nav className="h-16 bg-white border-b border-gray-100 px-8 flex items-center justify-between sticky top-0 z-50 shadow-sm">
      <div className="flex items-center gap-4">
        <div className="bg-primary p-2 rounded-xl">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <div>
          <h1 className="text-xl font-black text-gray-900 tracking-tight">DreamTalk</h1>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest leading-none">{moduleName}</p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
          <span className="text-xs font-bold text-gray-500 uppercase tracking-tighter">System Online</span>
        </div>
      </div>
    </nav>
  );
};
