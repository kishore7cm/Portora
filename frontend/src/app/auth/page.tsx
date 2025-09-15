'use client';

import { useState } from 'react';

export default function AuthPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (email === 'demo@portora.com' && password === '123456') {
      // Simple redirect
      window.location.href = '/dashboard';
    } else {
      setError('Invalid email or password');
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      backgroundColor: '#f3f4f6',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
        padding: '32px'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <h1 style={{ 
            fontSize: '24px', 
            fontWeight: 'bold', 
            color: '#1e40af', 
            marginBottom: '8px' 
          }}>
            Welcome to Portora
          </h1>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>
            Sign in to continue
          </p>
        </div>
        
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '16px',
                boxSizing: 'border-box'
              }}
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '16px',
                boxSizing: 'border-box'
              }}
            />
          </div>
          {error && <p style={{ color: '#ef4444', fontSize: '14px', margin: 0 }}>{error}</p>}

          <button
            type="submit"
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: '#1e40af',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            Login
          </button>
          
          <div style={{ textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
            <p>Demo credentials: demo@portora.com / 123456</p>
          </div>
        </form>
      </div>
    </div>
  );
}