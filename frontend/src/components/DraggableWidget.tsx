'use client';

import { useState, useRef, useEffect } from 'react';
import { GripVertical, X } from 'lucide-react';

interface DraggableWidgetProps {
  id: string;
  title: string;
  children: React.ReactNode;
  onRemove?: (id: string) => void;
  onMove?: (id: string, newPosition: { x: number; y: number }) => void;
  position?: { x: number; y: number };
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export default function DraggableWidget({
  id,
  title,
  children,
  onRemove,
  onMove,
  position = { x: 0, y: 0 },
  size = 'medium',
  className = ''
}: DraggableWidgetProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [currentPosition, setCurrentPosition] = useState(position);
  const widgetRef = useRef<HTMLDivElement>(null);

  const sizeClasses = {
    small: 'w-64 h-48',
    medium: 'w-80 h-64',
    large: 'w-96 h-80'
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target !== e.currentTarget) return;
    
    setIsDragging(true);
    const rect = widgetRef.current?.getBoundingClientRect();
    if (rect) {
      setDragOffset({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;

    const newPosition = {
      x: e.clientX - dragOffset.x,
      y: e.clientY - dragOffset.y
    };

    setCurrentPosition(newPosition);
    onMove?.(id, newPosition);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  return (
    <div
      ref={widgetRef}
      className={`
        absolute bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700
        ${sizeClasses[size]}
        ${isDragging ? 'z-50 shadow-2xl' : 'z-10'}
        ${className}
      `}
      style={{
        left: currentPosition.x,
        top: currentPosition.y,
        transform: isDragging ? 'rotate(2deg)' : 'none',
        transition: isDragging ? 'none' : 'transform 0.2s ease'
      }}
      onMouseDown={handleMouseDown}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 rounded-t-lg">
        <div className="flex items-center space-x-2">
          <GripVertical className="w-4 h-4 text-gray-400 cursor-move" />
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">{title}</h3>
        </div>
        {onRemove && (
          <button
            onClick={() => onRemove(id)}
            className="text-gray-400 hover:text-red-500 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="p-4 h-full overflow-auto">
        {children}
      </div>
    </div>
  );
}
