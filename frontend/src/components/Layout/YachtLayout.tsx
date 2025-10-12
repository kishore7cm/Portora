"use client";
import React from "react";
import YachtFooter from "./YachtFooter";

interface YachtLayoutProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

export default function YachtLayout({ title, subtitle, children }: YachtLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFBF7] to-[#EDE9E3] p-6 md:p-10 font-inter">
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
