import React from 'react';
import ProductCard from './ProductCard';

const ProductGrid = ({ title, subtitle, products, strategy }) => {
  if (!products || products.length === 0) return null;

  const strategyLabel = {
    cold_start: { text: 'Popularity Engine', color: 'bg-amber-100 text-amber-700' },
    personalized: { text: 'Hybrid AI Engine', color: 'bg-indigo-100 text-indigo-700' },
    content_based: { text: 'Content Engine', color: 'bg-emerald-100 text-emerald-700' },
  };

  const label = strategyLabel[strategy];

  return (
    <section className="py-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-2">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">{title}</h2>
          {subtitle && <p className="text-sm text-slate-500 mt-1">{subtitle}</p>}
        </div>
        {label && (
          <span className={`${label.color} text-xs font-semibold px-3 py-1.5 rounded-full self-start`}>
            ⚡ {label.text}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        {products.map((product) => (
          <ProductCard key={product.asin} product={product} isRecommended={true} />
        ))}
      </div>
    </section>
  );
};

export default ProductGrid;
