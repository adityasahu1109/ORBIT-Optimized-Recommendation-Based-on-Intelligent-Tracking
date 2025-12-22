import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 pt-12 pb-8 mt-auto">
      <div className="container mx-auto px-4">
        
        {/* Top Section: Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          
          {/* Column 1: Brand & About */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">🪐</span>
              <span className="text-xl font-bold text-gray-900 tracking-tight">
                ORBIT
              </span>
            </div>
            <p className="text-gray-500 text-sm leading-relaxed max-w-xs">
              An intelligent e-commerce demonstration powered by Machine Learning. 
              Featuring Content-Based Filtering, Collaborative Filtering, and Popularity engines.
            </p>
          </div>

          {/* Column 2: Quick Links */}
          <div>
            <h3 className="text-gray-900 font-semibold mb-4">Explore</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <Link to="/" className="hover:text-blue-600 transition-colors">
                  Home & Recommendations
                </Link>
              </li>
              <li>
                <Link to="/cart" className="hover:text-blue-600 transition-colors">
                  Shopping Cart
                </Link>
              </li>
              <li>
                <Link to="/search?q=electronics" className="hover:text-blue-600 transition-colors">
                  Search Products
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 3: Connect (Simulated) */}
          <div>
            <h3 className="text-gray-900 font-semibold mb-4">Connect</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center gap-2">
                <span>GitHub:</span>
                <a href="#" className="text-blue-600 hover:underline">/orbit-recommender</a>
              </li>
              <li className="flex items-center gap-2">
                <span>Email:</span>
                <a href="mailto:dev@example.com" className="text-blue-600 hover:underline">dev@example.com</a>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <hr className="border-gray-100 my-8" />

        {/* Bottom Section: Copyright */}
        <div className="flex flex-col md:flex-row justify-between items-center text-xs text-gray-400">
          <p>© {new Date().getFullYear()} ORBIT Recommender. Built for educational purposes.</p>
          <div className="flex gap-4 mt-4 md:mt-0">
            <span className="hover:text-gray-600 cursor-pointer">Privacy Policy</span>
            <span className="hover:text-gray-600 cursor-pointer">Terms of Service</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;