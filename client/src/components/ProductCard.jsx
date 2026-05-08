import React from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { Star, ExternalLink } from 'lucide-react';

const ProductCard = ({ product, isRecommended = false }) => {
  const { userId } = useUser();

  const getValidImage = (url, title) => {
    if (!url || url === '0' || !String(url).startsWith('http')) {
      const safeTitle = title.split(',')[0].trim().substring(0, 20).replace(/\s/g, '+');
      return `https://placehold.co/400x300/1e293b/94a3b8?text=${safeTitle}`;
    }
    return url;
  };

  const getStrategyBadge = (reason) => {
    if (!reason) return null;
    if (reason.includes('Trending')) return { text: '🔥 Trending', color: 'bg-amber-500/10 text-amber-400 border-amber-500/20' };
    if (reason.includes('interest')) return { text: '✨ For You', color: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' };
    if (reason.includes('Similar')) return { text: '🔗 Similar', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' };
    if (reason.includes('Popular')) return { text: '📈 Popular', color: 'bg-sky-500/10 text-sky-400 border-sky-500/20' };
    return { text: '💡 Picked', color: 'bg-slate-500/10 text-slate-400 border-slate-500/20' };
  };

  const badge = getStrategyBadge(product.reason);

  return (
    <Link
      to={`/product/${product.asin}`}
      state={{ product, userId }}
      className="group flex flex-col bg-white rounded-2xl shadow-sm border border-slate-200/80 overflow-hidden hover:shadow-xl hover:shadow-slate-200/50 hover:-translate-y-1 transition-all duration-300 h-full"
    >
      {/* Badge */}
      {badge && (
        <div className={`${badge.color} text-xs px-3 py-1.5 font-semibold border-b flex items-center gap-1`}>
          {badge.text}
        </div>
      )}

      {/* Image */}
      <div className="h-48 w-full bg-slate-50 p-5 flex items-center justify-center relative overflow-hidden">
        <img
          src={getValidImage(product.imgUrl, product.title)}
          alt={product.title}
          className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col flex-grow">
        <h3
          className="text-sm font-semibold text-slate-800 line-clamp-2 mb-2 min-h-[2.5rem] group-hover:text-indigo-700 transition-colors"
          title={product.title}
        >
          {product.title}
        </h3>

        <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
          <div className="flex items-center gap-0.5 text-amber-500">
            <Star size={12} fill="currentColor" />
            <span className="font-medium">{product.stars || '0'}</span>
          </div>
          <span className="text-slate-300">•</span>
          <span>{(product.reviews || 0).toLocaleString()} reviews</span>
        </div>

        <div className="mt-auto flex items-center justify-between pt-3 border-t border-slate-100">
          <span className="text-lg font-bold text-slate-900">
            ${product.price || 'N/A'}
          </span>
          <span className="text-indigo-600 text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            View <ExternalLink size={12} />
          </span>
        </div>
      </div>
    </Link>
  );
};

export default ProductCard;