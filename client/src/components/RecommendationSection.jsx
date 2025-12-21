import React from 'react';
import ProductCard from './ProductCard';

const RecommendationSection = ({ title, products }) => {
  if (!products || products.length === 0) return null;

  return (
    <section className="py-8">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard 
              key={product.asin} 
              product={product} 
              isRecommended={true} 
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default RecommendationSection;