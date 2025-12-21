import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import ProductDetails from './pages/ProductDetails';
import SearchResults from './pages/SearchResults'; // <--- 1. Import this!
import Footer from './components/Footer';

function App() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/product/:asin" element={<ProductDetails />} />
          {/* 2. Add this Route below! */}
          <Route path="/search" element={<SearchResults />} /> 
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;