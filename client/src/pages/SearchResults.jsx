import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchProducts } from '../services/api';
import ProductCard from '../components/ProductCard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { Search, ChevronDown } from 'lucide-react';

const INITIAL_DISPLAY = 12;
const LOAD_MORE_COUNT = 12;

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q');

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [visibleCount, setVisibleCount] = useState(INITIAL_DISPLAY);

  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      setVisibleCount(INITIAL_DISPLAY);
      if (query) {
        const data = await searchProducts(query);
        setResults(data);
      }
      setLoading(false);
    };
    fetchResults();
  }, [query]);

  const visibleProducts = results.slice(0, visibleCount);
  const hasMore = visibleCount < results.length;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white pb-20">

      {/* Search Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-50 rounded-lg">
              <Search size={20} className="text-indigo-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-800">
                Search Results for <span className="text-indigo-600">"{query}"</span>
              </h1>
              {!loading && (
                <p className="text-sm text-slate-500 mt-0.5">
                  {results.length > 0
                    ? `Found ${results.length} products — ranked by relevance × quality`
                    : 'No products found'}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <LoadingSkeleton count={8} />
        ) : visibleProducts.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
              {visibleProducts.map((product) => (
                <ProductCard key={product.asin} product={product} />
              ))}
            </div>

            {/* Show More Button */}
            {hasMore && (
              <div className="flex justify-center mt-10">
                <button
                  onClick={() => setVisibleCount(prev => prev + LOAD_MORE_COUNT)}
                  className="group flex items-center gap-2 px-8 py-3 bg-white border-2 border-indigo-200 text-indigo-700 rounded-xl font-semibold text-sm hover:bg-indigo-50 hover:border-indigo-400 transition-all duration-200 shadow-sm hover:shadow-md"
                >
                  Show More Results
                  <ChevronDown size={18} className="group-hover:translate-y-0.5 transition-transform" />
                  <span className="text-indigo-400 font-normal ml-1">
                    ({results.length - visibleCount} remaining)
                  </span>
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-20">
            <div className="bg-slate-50 rounded-2xl p-10 max-w-md mx-auto border border-slate-200">
              <Search size={48} className="text-slate-300 mx-auto mb-4" />
              <p className="text-lg font-medium text-slate-700 mb-2">No products found</p>
              <p className="text-sm text-slate-500">
                Try checking your spelling or using more general keywords.
                <br />
                The search uses TF-IDF, so partial word matches will also work.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchResults;