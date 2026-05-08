import React from 'react';

const LoadingSkeleton = ({ count = 8 }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden animate-pulse"
        >
          {/* Image placeholder */}
          <div className="h-48 bg-slate-100" />

          {/* Content placeholder */}
          <div className="p-4 space-y-3">
            <div className="h-4 bg-slate-100 rounded-full w-full" />
            <div className="h-4 bg-slate-100 rounded-full w-3/4" />

            <div className="flex items-center gap-2">
              <div className="h-3 bg-slate-100 rounded-full w-12" />
              <div className="h-3 bg-slate-100 rounded-full w-16" />
            </div>

            <div className="pt-3 border-t border-slate-100">
              <div className="h-6 bg-slate-100 rounded-full w-20" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default LoadingSkeleton;
