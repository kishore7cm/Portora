'use client';

interface SkeletonProps {
  className?: string;
  children?: React.ReactNode;
}

export function Skeleton({ className = '', children }: SkeletonProps) {
  return (
    <div className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`}>
      {children}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <Skeleton className="h-4 w-1/4 mb-4" />
      <Skeleton className="h-8 w-1/2 mb-2" />
      <Skeleton className="h-4 w-3/4" />
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex space-x-4">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-28" />
        </div>
      </div>
      
      {/* Rows */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {Array.from({ length: rows }).map((_, index) => (
          <div key={index} className="px-6 py-4">
            <div className="flex space-x-4">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-16" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <Skeleton className="h-6 w-1/3 mb-4" />
      <div className="h-64 flex items-center justify-center">
        <div className="w-full h-full flex items-end justify-center space-x-2">
          {Array.from({ length: 8 }).map((_, index) => (
            <Skeleton
              key={index}
              className="w-8"
              style={{ height: `${Math.random() * 200 + 50}px` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export function PieChartSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <Skeleton className="h-6 w-1/3 mb-4" />
      <div className="h-64 flex items-center justify-center">
        <Skeleton className="w-48 h-48 rounded-full" />
      </div>
    </div>
  );
}

export function StatsCardSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <div className="flex items-center">
        <Skeleton className="w-12 h-12 rounded-lg mr-4" />
        <div className="flex-1">
          <Skeleton className="h-4 w-24 mb-2" />
          <Skeleton className="h-8 w-16" />
        </div>
      </div>
    </div>
  );
}

export function PortfolioSummarySkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {Array.from({ length: 4 }).map((_, index) => (
        <StatsCardSkeleton key={index} />
      ))}
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-48" />
        </div>
        <Skeleton className="h-8 w-32" />
      </div>

      {/* Stats Cards */}
      <PortfolioSummarySkeleton />

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PieChartSkeleton />
        <ChartSkeleton />
        <TableSkeleton />
        <CardSkeleton />
      </div>
    </div>
  );
}

export function AlertsSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 max-h-96 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <Skeleton className="w-5 h-5" />
          <Skeleton className="h-5 w-16" />
          <Skeleton className="w-6 h-6 rounded-full" />
        </div>
        <Skeleton className="w-4 h-4" />
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="p-4 border-l-4 border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 rounded">
            <div className="flex items-start space-x-3">
              <Skeleton className="w-5 h-5 mt-0.5" />
              <div className="flex-1">
                <Skeleton className="h-4 w-3/4 mb-2" />
                <Skeleton className="h-3 w-full mb-2" />
                <div className="flex space-x-2">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-3 w-12" />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
