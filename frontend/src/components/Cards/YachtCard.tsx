"use client";
import React from "react";

interface YachtCardProps {
  title: string;
  subtitle?: string;
  borderColor?: string;
  children: React.ReactNode;
  className?: string;
}

export function YachtCard({ 
  title, 
  subtitle, 
  borderColor = "#C9A66B", 
  children, 
  className = "" 
}: YachtCardProps) {
  return (
    <div
      className={`p-6 rounded-2xl bg-[#FDFBF7] border shadow-[0_2px_6px_rgba(28,61,90,0.08)] hover:shadow-md transition-all duration-300 ${className}`}
      style={{ borderLeft: `4px solid ${borderColor}` }}
    >
      <p className="text-[#1C3D5A] font-semibold">{title}</p>
      {subtitle && <p className="text-[#5A6A73] text-sm mb-3">{subtitle}</p>}
      {children}
    </div>
  );
}
