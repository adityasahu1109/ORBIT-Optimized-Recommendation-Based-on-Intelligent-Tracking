import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 pt-12 pb-8 mt-auto border-t border-slate-800">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">🪐</span>
              <span className="text-xl font-bold text-white tracking-tight">ORBIT</span>
            </div>
            <p className="text-sm leading-relaxed max-w-xs">
              An intelligent e-commerce recommendation engine powered by SVD Collaborative Filtering,
              TF-IDF Content Similarity, and Popularity-based ranking.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Explore</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="hover:text-indigo-400 transition-colors">
                  Home & Recommendations
                </Link>
              </li>
              <li>
                <Link to="/cart" className="hover:text-indigo-400 transition-colors">
                  Shopping Cart
                </Link>
              </li>
              <li>
                <Link to="/search?q=electronics" className="hover:text-indigo-400 transition-colors">
                  Search Products
                </Link>
              </li>
            </ul>
          </div>

          {/* Tech */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Built With</h3>
            <div className="flex flex-wrap gap-2">
              {['FastAPI', 'Surprise SVD', 'scikit-learn', 'React', 'TailwindCSS', 'SQLite'].map((tech) => (
                <span
                  key={tech}
                  className="bg-slate-800 text-slate-300 text-xs px-2.5 py-1 rounded-full border border-slate-700"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>

        <hr className="border-slate-800 my-8" />

        <div className="flex flex-col md:flex-row justify-between items-center text-xs text-slate-500">
          <p>© {new Date().getFullYear()} ORBIT Recommender. Built for educational purposes.</p>
          <p className="mt-2 md:mt-0">
            Train-once architecture · SVD + TF-IDF + Popularity hybrid engine
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;