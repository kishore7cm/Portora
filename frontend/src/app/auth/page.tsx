'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AuthPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSignup, setIsSignup] = useState(false);

  const loadUsers = (): Record<string, string> => {
    if (typeof window === 'undefined') return {};
    try {
      const raw = localStorage.getItem('users');
      const parsed = raw ? JSON.parse(raw) : {};
      // Seed demo user if missing
      if (!parsed['demo@portora.com']) {
        parsed['demo@portora.com'] = '123456';
      }
      return parsed;
    } catch {
      return { 'demo@portora.com': '123456' };
    }
  };

  const saveUsers = (users: Record<string, string>) => {
    if (typeof window === 'undefined') return;
    localStorage.setItem('users', JSON.stringify(users));
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const eLower = email.trim().toLowerCase();
    const pTrim = password.trim();
    const users = loadUsers();
    const ok = users[eLower] && users[eLower] === pTrim;

    if (ok) {
      if (typeof window !== 'undefined') {
        localStorage.setItem('loggedIn', 'true');
        localStorage.setItem('userEmail', eLower);
      }
      router.push('/dashboard');
    } else {
      setError('❌ Invalid email or password');
    }
  };

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const eLower = email.trim().toLowerCase();
    const pTrim = password.trim();
    if (!eLower || !pTrim) {
      setError('❌ Please enter email and password');
      return;
    }
    if (pTrim.length < 4) {
      setError('❌ Password must be at least 4 characters');
      return;
    }
    const users = loadUsers();
    if (users[eLower]) {
      setError('❌ Account already exists');
      return;
    }
    users[eLower] = pTrim;
    saveUsers(users);
    if (typeof window !== 'undefined') {
      localStorage.setItem('loggedIn', 'true');
      localStorage.setItem('userEmail', eLower);
    }
    router.push('/dashboard');
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #e3f2fd 0%, #ffffff 50%, #e8f5e8 100%)',
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
            {isSignup ? 'Create your account' : 'Sign in to continue'}
          </p>
        </div>
        
        <form onSubmit={isSignup ? handleSignup : handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
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
            {isSignup ? 'Create Account' : 'Login'}
          </button>
          
          <div style={{ textAlign: 'center', fontSize: '14px', color: '#6b7280' }}>
            {isSignup ? (
              <button 
                type="button" 
                onClick={() => setIsSignup(false)} 
                style={{ 
                  color: '#1e40af', 
                  textDecoration: 'underline', 
                  background: 'none', 
                  border: 'none', 
                  cursor: 'pointer' 
                }}
              >
                Have an account? Sign in
              </button>
            ) : (
              <button 
                type="button" 
                onClick={() => setIsSignup(true)} 
                style={{ 
                  color: '#1e40af', 
                  textDecoration: 'underline', 
                  background: 'none', 
                  border: 'none', 
                  cursor: 'pointer' 
                }}
              >
                Create account
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}