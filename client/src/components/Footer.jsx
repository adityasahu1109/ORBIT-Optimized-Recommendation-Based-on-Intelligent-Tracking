import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-8">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          
          {/* Brand / Logo Area */}
          <div className="mb-4 md:mb-0">
            <h2 className="text-xl font-bold">MyPortfolio</h2>
            <p className="text-gray-400 text-sm mt-1">
              Building digital experiences.
            </p>
          </div>

          {/* Social Links */}
          <div className="flex space-x-6">
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-gray-400 hover:text-white transition-colors"
            >
              GitHub
            </a>
            <a 
              href="https://linkedin.com" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-gray-400 hover:text-white transition-colors"
            >
              LinkedIn
            </a>
            <a 
              href="mailto:user@example.com" 
              className="text-gray-400 hover:text-white transition-colors"
            >
              Email
            </a>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500 text-sm">
          &copy; {new Date().getFullYear()} All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;