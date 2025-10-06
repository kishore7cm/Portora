'use client'

import { useEffect, useState } from 'react';

export default function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Check if user is already logged in
    const isLoggedIn = localStorage.getItem('loggedIn') === 'true';
    if (isLoggedIn) {
      // Redirect to dashboard if already logged in
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1000);
    } else {
      // Redirect to auth if not logged in
      setTimeout(() => {
        window.location.href = '/auth';
      }, 1000);
    }
  }, []);

  if (!mounted) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#f3f4f6'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h1>Loading...</h1>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      backgroundColor: '#f3f4f6'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1>Wealtheon Portfolio Management</h1>
        <p>Redirecting...</p>
        <a href="/auth">Click here if not redirected</a>
      </div>
    </div>
  );
}