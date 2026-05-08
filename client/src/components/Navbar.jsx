import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { Search, ShoppingCart, ChevronDown } from 'lucide-react';

const Navbar = () => {
  const [query, setQuery] = useState('');
  const [showSimulator, setShowSimulator] = useState(false);
  const navigate = useNavigate();
  const { userId, setUserId, cartCount, switchToColdUser } = useUser();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query)}`);
      setQuery('');
    }
  };

  return (
    <nav className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 sticky top-0 z-50 shadow-lg shadow-slate-900/20">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">

          {/* Brand */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <span className="text-2xl group-hover:rotate-12 transition-transform duration-300">🪐</span>
            <div>
              <span className="text-xl font-extrabold text-white tracking-tight">ORBIT</span>
              <span className="text-xs text-slate-400 block -mt-1 font-medium tracking-widest uppercase">Recommender</span>
            </div>
          </Link>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-lg mx-8 relative">
            <input
              type="text"
              placeholder="Search products..."
              className="w-full bg-slate-700/50 text-white placeholder-slate-400 rounded-full py-2.5 pl-5 pr-12 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-slate-700 transition-all border border-slate-600/50"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button
              type="submit"
              className="absolute right-1.5 top-1/2 -translate-y-1/2 bg-indigo-600 hover:bg-indigo-500 text-white p-2 rounded-full transition-colors"
            >
              <Search size={16} />
            </button>
          </form>

          {/* Right Actions */}
          <div className="flex items-center gap-4">

            {/* User Simulator Toggle */}
            <div className="relative">
              <button
                onClick={() => setShowSimulator(!showSimulator)}
                className="flex items-center gap-2 bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg transition-colors text-sm border border-slate-600/50"
              >
                <div className="w-6 h-6 rounded-full bg-indigo-600/80 flex items-center justify-center text-white text-xs font-bold">
                  {userId.slice(0, 2)}
                </div>
                <span className="hidden lg:inline">User {userId}</span>
                <ChevronDown size={14} className={`transition-transform ${showSimulator ? 'rotate-180' : ''}`} />
              </button>

              {/* Dropdown */}
              {showSimulator && (
                <div className="absolute right-0 top-full mt-2 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl p-4 w-72 z-50">
                  <h3 className="text-white font-semibold text-sm mb-3 flex items-center gap-2">
                    <span className="text-indigo-400">⚙</span> User Simulation Panel
                  </h3>

                  <label className="text-xs text-slate-400 block mb-1.5">User ID</label>
                  <input
                    type="text"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 border border-slate-600 mb-3"
                  />

                  <div className="grid grid-cols-3 gap-2 mb-3">
                    {['1001', '1025', '1050'].map((id) => (
                      <button
                        key={id}
                        onClick={() => { setUserId(id); setShowSimulator(false); }}
                        className={`text-xs px-2 py-1.5 rounded-lg transition-colors font-medium ${
                          userId === id
                            ? 'bg-indigo-600 text-white'
                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                        }`}
                      >
                        User {id}
                      </button>
                    ))}
                  </div>

                  <button
                    onClick={() => { switchToColdUser(); setShowSimulator(false); }}
                    className="w-full text-xs bg-amber-600/20 text-amber-400 hover:bg-amber-600/30 px-3 py-2 rounded-lg transition-colors font-medium border border-amber-600/30"
                  >
                    🧊 Switch to Cold User (9999)
                  </button>

                  <p className="text-xs text-slate-500 mt-3">
                    Change the user ID to see different recommendations. Cold users have no interaction history.
                  </p>
                </div>
              )}
            </div>

            {/* Cart */}
            <Link
              to="/cart"
              className="relative flex items-center gap-1.5 text-slate-300 hover:text-white transition-colors"
            >
              <ShoppingCart size={20} />
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-indigo-600 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center animate-pulse">
                  {cartCount}
                </span>
              )}
            </Link>
          </div>
        </div>

        {/* Mobile Search */}
        <form onSubmit={handleSearch} className="md:hidden pb-3 flex gap-2">
          <input
            type="text"
            placeholder="Search products..."
            className="flex-1 bg-slate-700/50 text-white placeholder-slate-400 rounded-full py-2 pl-4 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 border border-slate-600/50 text-sm"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="bg-indigo-600 text-white p-2 rounded-full">
            <Search size={16} />
          </button>
        </form>
      </div>
    </nav>
  );
};

export default Navbar;