import React from 'react';
import { Link } from 'react-router-dom'; // <--- 1. Import Link

const ProductCard = ({ product, isRecommended = false }) => {
  const getValidImage = (url, title) => {
    if (!url || url === "0" || !url.startsWith("http")) {
      const safeTitle = title.split(",")[0].trim().substring(0, 20).replace(/\s/g, "+");
      return `https://placehold.co/400x300/EEE/31343C?text=${safeTitle}`;
    }
    return url;
  };

  // 2. We use state={{ product }} to pass data to the next page
  return (
    <Link 
      to={`/product/${product.asin}`} 
      state={{ product, userId: "1001" }} // Note: In a real app, userId should come from context
      className={`flex flex-col bg-white rounded-lg shadow-sm border overflow-hidden hover:shadow-md transition-shadow duration-300 h-full ${isRecommended ? 'border-blue-500 ring-1 ring-blue-100' : 'border-gray-200'}`}
    >
      
      {/* Recommended Badge */}
      {product.reason && (
        <div className="bg-blue-50 text-blue-700 text-xs px-3 py-1 font-medium border-b border-blue-100">
          {product.reason.replace("Because", "⚡ Because")}
        </div>
      )}

      {/* Image */}
      <div className="h-48 w-full bg-gray-100 p-4 flex items-center justify-center">
        <img 
          src={getValidImage(product.imgUrl, product.title)} 
          alt={product.title} 
          className="max-h-full max-w-full object-contain"
        />
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col flex-grow">
        <h3 className="text-sm font-semibold text-gray-900 line-clamp-2 mb-2 min-h-[2.5rem]" title={product.title}>
          {product.title}
        </h3>

        <div className="flex items-center space-x-2 text-xs text-gray-600 mb-2">
          <span className="text-yellow-500 flex items-center">★ {product.stars || '0'}</span>
          <span>({product.reviews || 0} reviews)</span>
        </div>

        <div className="mt-auto flex items-center justify-between pt-3 border-t border-gray-100">
          <span className="text-lg font-bold text-gray-900">${product.price || 'N/A'}</span>
          <span className="text-blue-600 text-sm font-medium">View Details</span>
        </div>
      </div>
    </Link>
  );
};

export default ProductCard;