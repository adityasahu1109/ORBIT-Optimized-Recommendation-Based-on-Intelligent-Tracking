import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { getRecommendations } from '../services/api';
import ProductGrid from '../components/ProductGrid';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { Sparkles, Zap, Users } from 'lucide-react';

const Home = () => {
  const { userId } = useUser();
  const [recommendations, setRecommendations] = useState([]);
  const [strategy, setStrategy] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getRecommendations(userId);
        setRecommendations(data.recommendations);
        setStrategy(data.strategy);
      } catch (err) {
        setError('Failed to load recommendations. Is the backend running?');
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(() => fetchData(), 300);
    return () => clearTimeout(timeoutId);
  }, [userId]);

  const strategyInfo = {
    cold_start: {
      icon: <Zap size={20} className="text-amber-500" />,
      title: 'Trending Products',
      description: "You're a new user! Here are the most popular items right now.",
    },
    personalized: {
      icon: <Sparkles size={20} className="text-indigo-500" />,
      title: 'Personalized For You',
      description: 'Curated based on your browsing history and preferences.',
    },
  };

  const info = strategyInfo[strategy] || strategyInfo.personalized;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white pb-20">

      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 text-white">
        <div className="container mx-auto px-4 py-10">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-white/10 rounded-xl backdrop-blur-sm">
              {info.icon}
            </div>
            <div>
              <h1 className="text-2xl font-bold mb-1">
                {info.title}
                <span className="text-indigo-200 font-normal text-lg ml-2">
                  — User {userId}
                </span>
              </h1>
              <p className="text-indigo-200 text-sm">{info.description}</p>
            </div>
          </div>

          {/* Strategy indicator */}
          {strategy === 'cold_start' && (
            <div className="mt-6 bg-white/10 backdrop-blur-sm rounded-xl p-4 flex items-center gap-3 border border-white/10">
              <Users size={18} className="text-amber-300 flex-shrink-0" />
              <p className="text-sm text-indigo-100">
                <strong className="text-white">Cold Start Mode:</strong> This user has no interaction history.
                Start clicking products to build a personalized profile!
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 -mt-4">
        {loading ? (
          <div className="pt-8">
            <LoadingSkeleton count={8} />
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <div className="bg-red-50 text-red-700 rounded-2xl p-8 max-w-md mx-auto border border-red-200">
              <p className="font-medium text-lg mb-2">Connection Error</p>
              <p className="text-sm text-red-500">{error}</p>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 bg-red-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        ) : recommendations.length > 0 ? (
          <ProductGrid
            title={strategy === 'cold_start' ? '🔥 Trending Now' : '✨ Top Picks for You'}
            subtitle={
              strategy === 'personalized'
                ? 'Blending your preferences with overall product quality'
                : 'Most popular products across all categories'
            }
            products={recommendations}
            strategy={strategy}
          />
        ) : (
          <div className="text-center py-20 text-slate-500">
            <p className="text-xl mb-2">No recommendations available</p>
            <p className="text-sm">
              Try switching to a different User ID or ensure the backend is running.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;