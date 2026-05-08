import React, { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [userId, setUserId] = useState(() => {
    return localStorage.getItem('orbit_user_id') || '1001';
  });

  const [cartItems, setCartItems] = useState(() => {
    const saved = localStorage.getItem('orbit_cart');
    return saved ? JSON.parse(saved) : [];
  });

  // Persist userId changes
  useEffect(() => {
    localStorage.setItem('orbit_user_id', userId);
  }, [userId]);

  // Persist cart changes
  useEffect(() => {
    localStorage.setItem('orbit_cart', JSON.stringify(cartItems));
  }, [cartItems]);

  const addToCart = (product) => {
    setCartItems((prev) => {
      if (prev.find((item) => item.asin === product.asin)) return prev;
      return [...prev, product];
    });
  };

  const removeFromCart = (asin) => {
    setCartItems((prev) => prev.filter((item) => item.asin !== asin));
  };

  const clearCart = () => {
    setCartItems([]);
  };

  const cartCount = cartItems.length;

  const switchToColdUser = () => {
    setUserId('9999');
  };

  return (
    <UserContext.Provider
      value={{
        userId,
        setUserId,
        cartItems,
        cartCount,
        addToCart,
        removeFromCart,
        clearCart,
        switchToColdUser,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error('useUser must be used within UserProvider');
  return ctx;
};

export default UserContext;
