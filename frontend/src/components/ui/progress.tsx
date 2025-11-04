interface ProgressProps {
  value: number
  className?: string
}

export function Progress({ value, className = '' }: ProgressProps) {
  const clampedValue = Math.min(Math.max(value, 0), 100)
  
  return (
    <div className={`w-full bg-neutral-200 rounded-full h-2 overflow-hidden ${className}`}>
      <div 
        className="h-full bg-gradient-brand rounded-full transition-all duration-500"
        style={{ width: `${clampedValue}%` }}
      />
    </div>
  )
}

