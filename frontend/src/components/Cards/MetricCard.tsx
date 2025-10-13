"use client";
import React from "react";

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  isPositive?: boolean;
  isNegative?: boolean;
  icon?: React.ReactNode;
}

export function MetricCard({ 
  title, 
  value, 
  subtitle, 
  isPositive = false, 
  isNegative = false,
  icon 
}: MetricCardProps) {
  const valueColor = isPositive
    ? "text-[#22C55E]"
    : isNegative
    ? "text-[#DC2626]"
    : "text-[#1C3D5A]";

  return (
    <div className="p-5 rounded-2xl bg-[#FDFBF7] border border-[#E3DED5] shadow-[0_1px_3px_rgba(28,61,90,0.08)] hover:shadow-md hover:-translate-y-0.5 transition-all">
      {icon && (
        <div className="flex items-center mb-3">
          <div className="p-2 bg-[#EDE9E3] rounded-lg mr-3">
            {icon}
          </div>
          <p className="text-sm text-[#5A6A73]">{title}</p>
        </div>
      )}
      {!icon && <p className="text-sm text-[#5A6A73]">{title}</p>}
      <h2 className={`text-2xl font-semibold mt-1 ${valueColor}`}>{value}</h2>
      {subtitle && <p className="text-xs text-[#5A6A73] mt-1">{subtitle}</p>}
    </div>
  );
}
