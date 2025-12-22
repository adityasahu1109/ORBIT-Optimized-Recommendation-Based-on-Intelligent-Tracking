import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import RecommendationSection from '../components/RecommendationSection';
import { getRecommendations, logInteraction } from '../services/api';

const ProductDetails = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { product, userId } = location.state || {}; 

  const [similarProducts, setSimilarProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // State for visual feedback on button
  const [isAdded, setIsAdded] = useState(false);

  // --- RESTORED HELPER FUNCTION ---
  // This ensures images don't break if the URL is missing or "0"
  const getValidImage = (url, title) => {
    if (!url || url === "0" || !url.startsWith("http")) {
      const safeTitle = title.split(",")[0].trim().substring(0, 20).replace(/\s/g, "+");
      return `https://placehold.co/400x300/EEE/31343C?text=${safeTitle}`;
    }
    return url;
  };

  // Redirect if accessed directly without state
  useEffect(() => {
    if (!product) {
      navigate('/');
    }
  }, [product, navigate]);

  // Fetch Data & Log View
  useEffect(() => {
    if (product && userId) {
      const loadData = async () => {
        setLoading(true);
        // 1. Log that the user viewed this
        await logInteraction(userId, product.asin, 'view');
        
        // 2. Get Context-Aware Recommendations
        const results = await getRecommendations(userId, product.asin);
        setSimilarProducts(results);
        
        setLoading(false);
      };

      loadData();
    }
  }, [product, userId]);

  // --- ADD TO CART LOGIC ---
  const handleAddToCart = async () => {
    if (!isAdded) {
      // 1. Send specific "add_to_cart" signal to backend (Weight: 3.0)
      await logInteraction(userId, product.asin, 'add_to_cart');
      
      // 2. Save to Browser LocalStorage
      const existingCart = JSON.parse(localStorage.getItem('orbit_cart')) || [];
      
      // Check for duplicates
      if (!existingCart.find(item => item.asin === product.asin)) {
        const newCart = [...existingCart, product];
        localStorage.setItem('orbit_cart', JSON.stringify(newCart));
      }

      // 3. Show visual feedback
      setIsAdded(true);
      
      // 4. Reset button after 2 seconds
      setTimeout(() => setIsAdded(false), 2000);
    }
  };

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
            
            {/* Left: Image (Now using getValidImage!) */}
            <div className="md:w-1/3 bg-gray-100 p-8 flex items-center justify-center">
              <img 
                src={getValidImage(product.imgUrl, product.title)} 
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
                
                {/* Interactive Button */}
                <button 
                  onClick={handleAddToCart}
                  className={`px-8 py-3 rounded-lg transition-all text-lg font-medium w-full md:w-auto flex items-center justify-center gap-2 ${
                    isAdded 
                      ? "bg-green-600 text-white hover:bg-green-700" 
                      : "bg-gray-900 text-white hover:bg-black"
                  }`}
                >
                  {isAdded ? (
                    <>
                      <span>✓</span> Added to Cart
                    </>
                  ) : (
                    "Add to Cart"
                  )}
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