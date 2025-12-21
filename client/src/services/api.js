const API_URL = "http://127.0.0.1:8000";

/**
 * Fetch recommendations for a specific user.
 * Optional: Pass 'product_id_viewed' if the user is looking at a specific item.
 */
export const getRecommendations = async (userId, productIdViewed = null) => {
  try {
    const payload = {
      user_id: userId,
      n_recommendations: 8
    };

    if (productIdViewed) {
      payload.product_id_viewed = productIdViewed;
    }

    const response = await fetch(`${API_URL}/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error('Network response was not ok');
    
    const data = await response.json();
    return data.recommendations || [];
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    return [];
  }
};

/**
 * Search for products by keyword.
 */
export const searchProducts = async (query) => {
  try {
    const response = await fetch(`${API_URL}/search?query=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('Search failed');
    
    const data = await response.json();
    return data.results || [];
  } catch (error) {
    console.error("Error searching products:", error);
    return [];
  }
};

/**
 * Log user interactions (clicks) to the backend.
 */
export const logInteraction = async (userId, productId, action = "click") => {
  try {
    await fetch(`${API_URL}/log-interaction`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: String(userId),
        product_id: String(productId),
        interaction_type: action
      }),
    });
  } catch (error) {
    console.error("Error logging interaction:", error);
  }
};