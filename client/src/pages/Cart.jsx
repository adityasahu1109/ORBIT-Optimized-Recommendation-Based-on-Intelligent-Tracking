import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { logInteraction } from '../services/api';
import { Trash2, ShoppingBag, ArrowLeft } from 'lucide-react';

const Cart = () => {
  const { userId, cartItems, removeFromCart, clearCart, cartCount } = useUser();
  const navigate = useNavigate();

  const total = cartItems
    .reduce((acc, item) => acc + (parseFloat(item.price) || 0), 0)
    .toFixed(2);

  const handleCheckout = async () => {
    // Log all purchases
    for (const item of cartItems) {
      await logInteraction(userId, item.asin, 'purchase');
    }
    clearCart();
    navigate('/');
  };

  const getValidImage = (url, title) => {
    if (!url || url === '0' || !String(url).startsWith('http')) {
      const safeTitle = title.split(',')[0].trim().substring(0, 20).replace(/\s/g, '+');
      return `https://placehold.co/200x200/1e293b/94a3b8?text=${safeTitle}`;
    }
    return url;
  };

  if (cartItems.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex flex-col items-center justify-center">
        <div className="text-center">
          <ShoppingBag size={64} className="text-slate-200 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Your Cart is Empty</h2>
          <p className="text-slate-500 mb-6">Start exploring to find products you'll love!</p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200"
          >
            <ArrowLeft size={16} /> Start Shopping
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white py-12 pb-20">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">
          Shopping Cart
          <span className="text-lg font-normal text-slate-400 ml-2">({cartCount} items)</span>
        </h1>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Cart Items */}
          <div className="lg:w-2/3 space-y-3">
            {cartItems.map((item) => (
              <div
                key={item.asin}
                className="bg-white p-4 rounded-xl shadow-sm border border-slate-200/80 flex items-center justify-between hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-4">
                  <div className="w-20 h-20 bg-slate-50 rounded-lg overflow-hidden flex-shrink-0 flex items-center justify-center">
                    <img
                      src={getValidImage(item.imgUrl, item.title)}
                      alt={item.title}
                      className="max-w-full max-h-full object-contain"
                    />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800 line-clamp-1 max-w-md text-sm">
                      {item.title}
                    </h3>
                    <p className="text-slate-400 text-xs mt-0.5">
                      {item.category || item.categoryName}
                    </p>
                    <p className="font-bold text-slate-900 mt-1">${item.price}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeFromCart(item.asin)}
                  className="text-red-400 hover:text-red-600 hover:bg-red-50 p-2 rounded-lg transition-colors"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>

          {/* Checkout Summary */}
          <div className="lg:w-1/3">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200/80 sticky top-24">
              <h2 className="text-lg font-bold text-slate-800 mb-4">Order Summary</h2>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between text-slate-600">
                  <span>Subtotal ({cartCount} items)</span>
                  <span>${total}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Shipping</span>
                  <span className="text-emerald-600 font-medium">Free</span>
                </div>
              </div>

              <div className="border-t border-slate-100 pt-4 mt-4 flex justify-between items-center mb-6">
                <span className="text-xl font-bold text-slate-900">Total</span>
                <span className="text-xl font-bold text-slate-900">${total}</span>
              </div>

              <button
                onClick={handleCheckout}
                className="w-full bg-indigo-600 text-white py-3.5 rounded-xl font-bold hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200 text-sm"
              >
                Proceed to Checkout
              </button>

              <p className="text-xs text-slate-400 text-center mt-3">
                Purchase signals are sent to the AI engine for learning.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;