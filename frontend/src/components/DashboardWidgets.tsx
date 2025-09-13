'use client';

import { useState, useEffect } from 'react';
import { Plus, Settings, BarChart3, TrendingUp, PieChart, Table } from 'lucide-react';
import DraggableWidget from './DraggableWidget';
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, LineChart, Line } from 'recharts';

interface Widget {
  id: string;
  type: string;
  title: string;
  position: { x: number; y: number };
  size: 'small' | 'medium' | 'large';
  data?: any;
}

interface DashboardWidgetsProps {
  portfolioData?: any[];
  sp500Data?: any[];
  onWidgetUpdate?: (widgets: Widget[]) => void;
}

const sampleData = [
  { name: 'Stocks', value: 65, color: '#3B82F6' },
  { name: 'Bonds', value: 25, color: '#10B981' },
  { name: 'Cash', value: 10, color: '#F59E0B' }
];

const performanceData = [
  { month: 'Jan', value: 100 },
  { month: 'Feb', value: 105 },
  { month: 'Mar', value: 98 },
  { month: 'Apr', value: 112 },
  { month: 'May', value: 108 },
  { month: 'Jun', value: 115 }
];

export default function DashboardWidgets({ portfolioData, sp500Data, onWidgetUpdate }: DashboardWidgetsProps) {
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [showAddMenu, setShowAddMenu] = useState(false);
  const [nextId, setNextId] = useState(1);

  // Load widgets from localStorage on mount
  useEffect(() => {
    const savedWidgets = localStorage.getItem('dashboard-widgets');
    if (savedWidgets) {
      setWidgets(JSON.parse(savedWidgets));
    } else {
      // Default widgets
      setWidgets([
        {
          id: 'portfolio-chart',
          type: 'pie-chart',
          title: 'Portfolio Allocation',
          position: { x: 20, y: 20 },
          size: 'medium'
        },
        {
          id: 'performance-chart',
          type: 'line-chart',
          title: 'Performance Trend',
          position: { x: 420, y: 20 },
          size: 'medium'
        }
      ]);
    }
  }, []);

  // Save widgets to localStorage when they change
  useEffect(() => {
    localStorage.setItem('dashboard-widgets', JSON.stringify(widgets));
    onWidgetUpdate?.(widgets);
  }, [widgets, onWidgetUpdate]);

  const addWidget = (type: string, title: string) => {
    const newWidget: Widget = {
      id: `widget-${nextId}`,
      type,
      title,
      position: { x: 50 + (nextId * 50), y: 50 + (nextId * 50) },
      size: 'medium'
    };
    
    setWidgets(prev => [...prev, newWidget]);
    setNextId(prev => prev + 1);
    setShowAddMenu(false);
  };

  const removeWidget = (id: string) => {
    setWidgets(prev => prev.filter(widget => widget.id !== id));
  };

  const moveWidget = (id: string, newPosition: { x: number; y: number }) => {
    setWidgets(prev => prev.map(widget => 
      widget.id === id ? { ...widget, position: newPosition } : widget
    ));
  };

  const renderWidgetContent = (widget: Widget) => {
    switch (widget.type) {
      case 'pie-chart':
        return (
          <div className="h-full">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={sampleData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sampleData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        );

      case 'line-chart':
        return (
          <div className="h-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        );

      case 'bar-chart':
        return (
          <div className="h-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );

      case 'stats-card':
        return (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">$125,430</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Portfolio Value</div>
            <div className="text-green-600 text-sm mt-1">+12.5% this month</div>
          </div>
        );

      case 'table':
        return (
          <div className="h-full overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-2">Symbol</th>
                  <th className="text-right py-2">Value</th>
                </tr>
              </thead>
              <tbody>
                {['AAPL', 'MSFT', 'GOOGL', 'TSLA'].map(symbol => (
                  <tr key={symbol} className="border-b border-gray-100 dark:border-gray-800">
                    <td className="py-2">{symbol}</td>
                    <td className="text-right py-2">$1,234</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      default:
        return <div className="h-full flex items-center justify-center text-gray-500">Unknown widget type</div>;
    }
  };

  return (
    <div className="relative min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Add Widget Button */}
      <div className="fixed top-4 right-4 z-50">
        <div className="relative">
          <button
            onClick={() => setShowAddMenu(!showAddMenu)}
            className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-colors"
          >
            <Plus className="w-6 h-6" />
          </button>

          {showAddMenu && (
            <div className="absolute right-0 top-12 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-2 min-w-48">
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 px-2">Add Widget</div>
              <div className="space-y-1">
                <button
                  onClick={() => addWidget('pie-chart', 'Portfolio Allocation')}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 rounded flex items-center space-x-2"
                >
                  <PieChart className="w-4 h-4" />
                  <span>Pie Chart</span>
                </button>
                <button
                  onClick={() => addWidget('line-chart', 'Performance Trend')}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 rounded flex items-center space-x-2"
                >
                  <TrendingUp className="w-4 h-4" />
                  <span>Line Chart</span>
                </button>
                <button
                  onClick={() => addWidget('bar-chart', 'Bar Chart')}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 rounded flex items-center space-x-2"
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>Bar Chart</span>
                </button>
                <button
                  onClick={() => addWidget('stats-card', 'Portfolio Stats')}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 rounded flex items-center space-x-2"
                >
                  <Settings className="w-4 h-4" />
                  <span>Stats Card</span>
                </button>
                <button
                  onClick={() => addWidget('table', 'Data Table')}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 rounded flex items-center space-x-2"
                >
                  <Table className="w-4 h-4" />
                  <span>Data Table</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Widgets */}
      {widgets.map(widget => (
        <DraggableWidget
          key={widget.id}
          id={widget.id}
          title={widget.title}
          position={widget.position}
          size={widget.size}
          onRemove={removeWidget}
          onMove={moveWidget}
        >
          {renderWidgetContent(widget)}
        </DraggableWidget>
      ))}

      {/* Empty State */}
      {widgets.length === 0 && (
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No widgets yet</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">Add widgets to customize your dashboard</p>
            <button
              onClick={() => setShowAddMenu(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
            >
              Add Your First Widget
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
