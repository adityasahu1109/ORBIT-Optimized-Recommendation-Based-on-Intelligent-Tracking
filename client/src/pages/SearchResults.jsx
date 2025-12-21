import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchProducts } from '../services/api';
import ProductCard from '../components/ProductCard';

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q'); // Get "headphones" from URL
  
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      if (query) {
        const data = await searchProducts(query);
        setResults(data);
      }
      setLoading(false);
    };

    fetchResults();
  }, [query]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">
          Search Results for: <span className="text-blue-600">"{query}"</span>
        </h1>

        {loading ? (
          <div className="text-center py-20">Loading...</div>
        ) : (
          <>
            {results.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {results.map((product) => (
                  <ProductCard key={product.asin} product={product} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20 text-gray-500">
                <p className="text-xl">No products found matching "{query}".</p>
                <p className="mt-2">Try checking your spelling or using more general keywords.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default SearchResults;