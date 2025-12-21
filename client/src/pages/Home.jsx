import React, { useState, useEffect } from 'react';
import RecommendationSection from '../components/RecommendationSection';
import { getRecommendations, logInteraction } from '../services/api';

const Home = () => {
  // State for data and simulation
  const [recommendations, setRecommendations] = useState([]);
  const [userId, setUserId] = useState("1001"); // Default user from your prototype
  const [loading, setLoading] = useState(false);

  // Fetch recommendations whenever User ID changes
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await getRecommendations(userId);
        setRecommendations(data);
      } catch (error) {
        console.error("Failed to load home feed", error);
      } finally {
        setLoading(false);
      }
    };

    // Debounce slightly so we don't spam API while typing
    const timeoutId = setTimeout(() => fetchData(), 500);
    return () => clearTimeout(timeoutId);
  }, [userId]);

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      
      {/* Simulation Controls (Like your Streamlit Sidebar) */}
      <div className="bg-white border-b border-gray-200 py-4 px-6 shadow-sm mb-8">
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              🪐 ORBIT <span className="text-blue-600 font-light">Recommender</span>
            </h1>
            <p className="text-sm text-gray-500">AI-Powered Suggestion Engine</p>
          </div>
          
          <div className="flex items-center gap-3 bg-gray-100 p-2 rounded-lg">
            <span className="text-sm font-medium text-gray-600">Simulate User ID:</span>
            <input 
              type="text" 
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-24"
            />
            <button 
              onClick={() => setUserId("9999")}
              className="text-xs bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-gray-700 transition-colors"
            >
              Reset (Cold)
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4">
        
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {/* Recommendations Feed */}
            {recommendations.length > 0 ? (
              <RecommendationSection 
                title={`Top Picks for You (User ${userId})`} 
                products={recommendations} 
              />
            ) : (
              <div className="text-center py-20 text-gray-500">
                <p className="text-xl">No recommendations found.</p>
                <p className="text-sm">Try changing the User ID or check if the backend is running.</p>
              </div>
            )}
          </>
        )}

      </div>
    </div>
  );
};

export default Home;