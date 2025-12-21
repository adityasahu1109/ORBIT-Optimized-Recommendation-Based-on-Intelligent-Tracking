import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import RecommendationSection from '../components/RecommendationSection';
import { getRecommendations, logInteraction } from '../services/api';

const ProductDetails = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { product, userId } = location.state || {}; // Get data passed from the click

  const [similarProducts, setSimilarProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Safety check: If someone goes to this URL directly without clicking, send them home
  useEffect(() => {
    if (!product) {
      navigate('/');
    }
  }, [product, navigate]);

  // Fetch "Similar Items" and Log the View
  useEffect(() => {
    if (product && userId) {
      const loadData = async () => {
        setLoading(true);
        
        // 1. Log that the user viewed this (for the AI to learn)
        logInteraction(userId, product.asin, 'view');

        // 2. Get Context-Aware Recommendations
        const results = await getRecommendations(userId, product.asin);
        setSimilarProducts(results);
        
        setLoading(false);
      };

      loadData();
    }
  }, [product, userId]);

  if (!product) return null;

  return (
    <div className="min-h-screen bg-gray-50 pb-20 pt-8">
      <div className="container mx-auto px-4">
        
        {/* Back Button */}
        <button 
          onClick={() => navigate(-1)} 
          className="mb-6 text-gray-500 hover:text-gray-900 flex items-center gap-2"
        >
          &larr; Back to Feed
        </button>

        {/* Main Product Layout */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-12">
          <div className="flex flex-col md:flex-row">
            
            {/* Left: Image */}
            <div className="md:w-1/3 bg-gray-100 p-8 flex items-center justify-center">
              <img 
                src={product.imgUrl} 
                alt={product.title} 
                className="max-w-full max-h-96 object-contain mix-blend-multiply"
              />
            </div>

            {/* Right: Details */}
            <div className="md:w-2/3 p-8">
              <div className="mb-2">
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full font-bold uppercase tracking-wide">
                  {product.category || "Product"}
                </span>
              </div>
              
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.title}</h1>
              
              <div className="flex items-center gap-4 mb-6">
                <span className="text-2xl font-bold text-green-600">${product.price || 'N/A'}</span>
                <div className="flex items-center text-yellow-500">
                  <span className="text-xl">★</span>
                  <span className="ml-1 text-gray-700 font-medium">{product.stars}</span>
                  <span className="text-gray-400 text-sm ml-1">({product.reviews} reviews)</span>
                </div>
              </div>

              <div className="border-t border-gray-100 pt-6 mt-6">
                <p className="text-gray-600 leading-relaxed mb-6">
                  This product was recommended because: <span className="font-semibold text-blue-600">{product.reason || "It matches your profile"}</span>.
                </p>
                <button className="bg-gray-900 text-white px-8 py-3 rounded-lg hover:bg-black transition-colors text-lg font-medium w-full md:w-auto">
                  Add to Cart
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* "Similar Items" Section */}
        {loading ? (
          <div className="text-center py-10">Loading similar items...</div>
        ) : (
          <RecommendationSection 
            title="People who viewed this also liked" 
            products={similarProducts} 
          />
        )}
        
      </div>
    </div>
  );
};

export default ProductDetails;