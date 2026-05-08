import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { getRecommendations, logInteraction } from '../services/api';
import ProductGrid from '../components/ProductGrid';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { ArrowLeft, ShoppingCart, Check, Star, Tag } from 'lucide-react';

const ProductDetails = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userId, addToCart } = useUser();
  const { product } = location.state || {};

  const [similarProducts, setSimilarProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAdded, setIsAdded] = useState(false);

  const getValidImage = (url, title) => {
    if (!url || url === '0' || !String(url).startsWith('http')) {
      const safeTitle = title.split(',')[0].trim().substring(0, 20).replace(/\s/g, '+');
      return `https://placehold.co/500x400/1e293b/94a3b8?text=${safeTitle}`;
    }
    return url;
  };

  // Redirect if no product data
  useEffect(() => {
    if (!product) navigate('/');
  }, [product, navigate]);

  // Fetch similar products and log view
  useEffect(() => {
    if (product && userId) {
      const loadData = async () => {
        setLoading(true);
        await logInteraction(userId, product.asin, 'view');
        const data = await getRecommendations(userId, product.asin);
        setSimilarProducts(data.recommendations);
        setLoading(false);
      };
      loadData();
    }
  }, [product, userId]);

  const handleAddToCart = async () => {
    if (!isAdded) {
      await logInteraction(userId, product.asin, 'add_to_cart');
      addToCart(product);
      setIsAdded(true);
      setTimeout(() => setIsAdded(false), 2500);
    }
  };

  if (!product) return null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white pb-20">
      <div className="container mx-auto px-4 pt-8">

        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="mb-6 text-slate-500 hover:text-slate-900 flex items-center gap-2 group text-sm font-medium"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
          Back
        </button>

        {/* Product Detail Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200/80 overflow-hidden mb-12">
          <div className="flex flex-col md:flex-row">

            {/* Image */}
            <div className="md:w-2/5 bg-slate-50 p-10 flex items-center justify-center relative">
              <img
                src={getValidImage(product.imgUrl, product.title)}
                alt={product.title}
                className="max-w-full max-h-96 object-contain"
              />
            </div>

            {/* Details */}
            <div className="md:w-3/5 p-8 lg:p-10">
              {/* Category Badge */}
              <div className="mb-3">
                <span className="inline-flex items-center gap-1 bg-indigo-50 text-indigo-700 text-xs px-3 py-1 rounded-full font-semibold uppercase tracking-wide">
                  <Tag size={12} />
                  {product.category || product.categoryName || 'Product'}
                </span>
              </div>

              <h1 className="text-2xl lg:text-3xl font-bold text-slate-900 mb-4 leading-tight">
                {product.title}
              </h1>

              {/* Rating & Reviews */}
              <div className="flex items-center gap-4 mb-6">
                <div className="flex items-center gap-1.5 bg-amber-50 px-3 py-1.5 rounded-lg">
                  <Star size={16} fill="#f59e0b" className="text-amber-500" />
                  <span className="font-bold text-slate-800">{product.stars}</span>
                </div>
                <span className="text-slate-400 text-sm">
                  {(product.reviews || 0).toLocaleString()} reviews
                </span>
              </div>

              {/* Price */}
              <div className="mb-8">
                <span className="text-3xl font-bold text-slate-900">${product.price || 'N/A'}</span>
              </div>

              {/* Reason */}
              {product.reason && (
                <div className="bg-slate-50 rounded-xl p-4 mb-8 border border-slate-100">
                  <p className="text-sm text-slate-600">
                    <span className="font-semibold text-indigo-600">Why this?</span>{' '}
                    {product.reason}
                  </p>
                </div>
              )}

              {/* Add to Cart Button */}
              <button
                onClick={handleAddToCart}
                className={`px-8 py-3.5 rounded-xl transition-all text-base font-semibold w-full md:w-auto flex items-center justify-center gap-2.5 shadow-lg ${
                  isAdded
                    ? 'bg-emerald-600 text-white shadow-emerald-200 hover:bg-emerald-700'
                    : 'bg-slate-900 text-white shadow-slate-300 hover:bg-slate-800 hover:shadow-xl'
                }`}
              >
                {isAdded ? (
                  <>
                    <Check size={18} /> Added to Cart
                  </>
                ) : (
                  <>
                    <ShoppingCart size={18} /> Add to Cart
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Similar Products */}
        {loading ? (
          <div>
            <h2 className="text-2xl font-bold text-slate-800 mb-6">People who viewed this also liked</h2>
            <LoadingSkeleton count={4} />
          </div>
        ) : (
          <ProductGrid
            title="People who viewed this also liked"
            products={similarProducts}
            strategy="content_based"
          />
        )}
      </div>
    </div>
  );
};

export default ProductDetails;