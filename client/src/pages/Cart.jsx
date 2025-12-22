import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logInteraction } from '../services/api';

const Cart = () => {
  // FIX 1: Load Cart directly in useState (Lazy Initialization)
  // This avoids the "cascading render" warning completely.
  const [cartItems, setCartItems] = useState(() => {
    const saved = localStorage.getItem('orbit_cart');
    return saved ? JSON.parse(saved) : [];
  });

  // FIX 2: Calculate initial total directly based on the loaded cart
  const [total, setTotal] = useState(() => {
    const saved = localStorage.getItem('orbit_cart');
    const items = saved ? JSON.parse(saved) : [];
    return items.reduce((acc, item) => acc + (parseFloat(item.price) || 0), 0).toFixed(2);
  });

  const navigate = useNavigate();
  const userId = "1001"; 

  // Helper to update total whenever cart changes
  const calculateTotal = (items) => {
    const sum = items.reduce((acc, item) => acc + (parseFloat(item.price) || 0), 0);
    setTotal(sum.toFixed(2));
  };

  const removeItem = (asin) => {
    const updatedCart = cartItems.filter(item => item.asin !== asin);
    setCartItems(updatedCart);
    localStorage.setItem('orbit_cart', JSON.stringify(updatedCart));
    calculateTotal(updatedCart);
  };

  const handleCheckout = async () => {
    for (const item of cartItems) {
      await logInteraction(userId, item.asin, 'purchase');
    }
    localStorage.removeItem('orbit_cart');
    setCartItems([]);
    setTotal(0); 
    //alert("Purchase Successful! The AI will learn from this.");
    navigate('/');
  };

  if (cartItems.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Your Cart is Empty</h2>
        <Link to="/" className="text-blue-600 hover:underline">Start Shopping</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart ({cartItems.length} items)</h1>
        
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Cart Items List */}
          <div className="lg:w-2/3 space-y-4">
            {cartItems.map((item) => (
              <div key={item.asin} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-20 h-20 bg-gray-100 rounded overflow-hidden flex-shrink-0">
                    <img src={item.imgUrl} alt={item.title} className="w-full h-full object-contain mix-blend-multiply" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800 line-clamp-1 max-w-md">{item.title}</h3>
                    <p className="text-gray-500 text-sm">{item.category}</p>
                    <p className="font-bold text-green-600 mt-1">${item.price}</p>
                  </div>
                </div>
                <button 
                  onClick={() => removeItem(item.asin)}
                  className="text-red-500 hover:text-red-700 text-sm font-medium px-3 py-1 border border-red-200 rounded hover:bg-red-50 transition-colors"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>

          {/* Checkout Summary */}
          <div className="lg:w-1/3">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 sticky top-24">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Order Summary</h2>
              <div className="flex justify-between mb-2 text-gray-600">
                <span>Subtotal</span>
                <span>${total}</span>
              </div>
              <div className="flex justify-between mb-4 text-gray-600">
                <span>Shipping</span>
                <span>Free</span>
              </div>
              <div className="border-t border-gray-200 pt-4 flex justify-between items-center mb-6">
                <span className="text-xl font-bold text-gray-900">Total</span>
                <span className="text-xl font-bold text-gray-900">${total}</span>
              </div>
              
              <button 
                onClick={handleCheckout}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition-colors shadow-lg"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;