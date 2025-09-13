'use client';

import { useState, useEffect, useRef } from 'react';
import { Bell, X, Check, AlertCircle, Info, Zap, Bot, TrendingUp } from 'lucide-react';
import { AlertsSkeleton } from './LoadingSkeleton';

interface Alert {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  expires_at?: string;
  metadata: Record<string, any>;
}

interface AlertsDropdownProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AlertsDropdown({ isOpen, onClose }: AlertsDropdownProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      fetchAlerts();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/alerts');
      if (response.ok) {
        const data = await response.json();
        setAlerts(data);
        setUnreadCount(data.filter((alert: Alert) => !alert.is_read).length);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (alertId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/alerts/${alertId}/read`, {
        method: 'POST',
      });
      
      if (response.ok) {
        setAlerts(prev => 
          prev.map(alert => 
            alert.id === alertId ? { ...alert, is_read: true } : alert
          )
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const response = await fetch('http://localhost:8000/alerts/read-all', {
        method: 'POST',
      });
      
      if (response.ok) {
        setAlerts(prev => 
          prev.map(alert => ({ ...alert, is_read: true }))
        );
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Error marking all alerts as read:', error);
    }
  };

  const getAlertIcon = (type: string, priority: string) => {
    const iconClass = `w-5 h-5 ${
      priority === 'high' ? 'text-red-500' : 
      priority === 'medium' ? 'text-yellow-500' : 
      'text-blue-500'
    }`;

    switch (type) {
      case 'portfolio':
        return <TrendingUp className={iconClass} />;
      case 'bot':
        return <Bot className={iconClass} />;
      case 'market':
        return <Zap className={iconClass} />;
      default:
        return <Info className={iconClass} />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-l-red-500 bg-red-50';
      case 'medium':
        return 'border-l-yellow-500 bg-yellow-50';
      case 'low':
        return 'border-l-blue-500 bg-blue-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  if (!isOpen) return null;

  return (
    <div 
      ref={dropdownRef}
      className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-96 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Bell className="w-5 h-5 text-gray-600" />
          <h3 className="font-semibold text-gray-900">Alerts</h3>
          {unreadCount > 0 && (
            <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
              {unreadCount}
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              Mark all read
            </button>
          )}
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-h-80 overflow-y-auto">
        {loading ? (
          <AlertsSkeleton />
        ) : alerts.length === 0 ? (
          <div className="p-8 text-center">
            <Bell className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No alerts yet</p>
            <p className="text-sm text-gray-400">We'll notify you about important updates</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 hover:bg-gray-50 transition-colors border-l-4 ${getPriorityColor(alert.priority)} ${
                  !alert.is_read ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getAlertIcon(alert.type, alert.priority)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className={`text-sm font-medium ${!alert.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                          {alert.title}
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                        <div className="flex items-center space-x-2 mt-2">
                          <span className="text-xs text-gray-500">
                            {formatTimeAgo(alert.created_at)}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            alert.priority === 'high' ? 'bg-red-100 text-red-700' :
                            alert.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {alert.priority}
                          </span>
                        </div>
                      </div>
                      {!alert.is_read && (
                        <button
                          onClick={() => markAsRead(alert.id)}
                          className="ml-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                          title="Mark as read"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {alerts.length > 0 && (
        <div className="p-3 border-t border-gray-200 bg-gray-50">
          <button
            onClick={() => {
              // Navigate to full alerts page
              console.log('Navigate to alerts page');
            }}
            className="w-full text-center text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            View all alerts
          </button>
        </div>
      )}
    </div>
  );
}
