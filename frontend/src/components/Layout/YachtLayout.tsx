"use client";
import React, { useState } from "react";
import { Sun, Moon, User, LogIn, LogOut } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import YachtFooter from "./YachtFooter";

interface YachtLayoutProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

export default function YachtLayout({ title, subtitle, children }: YachtLayoutProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className={`min-h-screen bg-gradient-to-b from-[#FDFBF7] to-[#EDE9E3] p-6 md:p-10 font-inter ${isDarkMode ? 'dark' : ''}`}>
      {/* Top Right Header */}
      <div className="flex justify-between items-center mb-6">
        <div></div>
        <div className="flex items-center space-x-4">
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-lg bg-[#EDE9E3] hover:bg-[#C9A66B] transition-colors"
            title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {isDarkMode ? (
              <Sun className="w-5 h-5 text-[#1C3D5A]" />
            ) : (
              <Moon className="w-5 h-5 text-[#1C3D5A]" />
            )}
          </button>

          {/* Login/Profile Button */}
          {isAuthenticated ? (
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-[#EDE9E3]">
                <User className="w-4 h-4 text-[#1C3D5A]" />
                <span className="text-[#1C3D5A] font-medium text-sm">
                  {user?.displayName || user?.email}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-[#EDE9E3] hover:bg-[#C9A66B] transition-colors"
              >
                <LogOut className="w-4 h-4 text-[#1C3D5A]" />
                <span className="text-[#1C3D5A] font-medium">Logout</span>
              </button>
            </div>
          ) : (
            <button
              onClick={() => window.location.href = '/auth'}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-[#1C3D5A] hover:bg-[#C9A66B] transition-colors"
            >
              <LogIn className="w-4 h-4 text-white" />
              <span className="text-white font-medium">Login</span>
            </button>
          )}
        </div>
      </div>

      <header className="mb-8">
        <h1 className="text-3xl font-semibold text-[#1C3D5A]" style={{ fontFamily: 'Playfair Display, serif' }}>{title}</h1>
        {subtitle && <p className="text-[#5A6A73] mt-1">{subtitle}</p>}
        <div className="h-[1px] bg-[#C9A66B] w-full mt-3" />
      </header>
      <main className="space-y-8">{children}</main>
      <YachtFooter />
    </div>
  );
}
