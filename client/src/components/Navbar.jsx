import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      // Navigate to search results
      navigate(`/search?q=${encodeURIComponent(query)}`);
      setQuery(""); // Clear input
    }
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">🪐</span>
            <span className="text-xl font-bold text-gray-900 tracking-tight">
              ORBIT
            </span>
          </Link>

          {/* Search Bar (Hidden on small mobile screens) */}
          <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-lg mx-8 relative">
            <input
              type="text"
              placeholder="Search products..."
              className="w-full bg-gray-100 text-gray-900 rounded-full py-2 pl-4 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button 
              type="submit"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-blue-600"
            >
              🔍
            </button>
          </form>

          {/* Right Side Actions */}
          <div className="flex items-center gap-4">
            
            {/* Cart Link - NEW */}
            <Link to="/cart" className="flex items-center gap-1 text-gray-600 hover:text-blue-600 font-medium transition-colors">
              <span className="text-xl">🛒</span>
              <span>Cart</span>
            </Link>

            {/* User Profile Stub */}
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-sm border border-blue-200">
              U
            </div>
          </div>

        </div>
      </div>
    </nav>
  );
};

export default Navbar;