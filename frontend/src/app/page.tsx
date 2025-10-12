'use client'

import { useEffect, useState } from 'react';
import YachtLayout from '@/components/Layout/YachtLayout';

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
      <YachtLayout title="Loading..." subtitle="Initializing Wealtheon">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-primary">Loading...</h1>
        </div>
      </YachtLayout>
    );
  }

  return (
    <YachtLayout 
      title="Wealtheon Portfolio Management" 
      subtitle="Yacht Club Premium – Sophisticated Wealth Management"
    >
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-primary">Wealtheon Portfolio Management</h1>
        <p className="text-textSecondary mt-2">Redirecting...</p>
        <a href="/auth" className="text-accent hover:text-primary transition-colors">Click here if not redirected</a>
      </div>
    </YachtLayout>
  );
}