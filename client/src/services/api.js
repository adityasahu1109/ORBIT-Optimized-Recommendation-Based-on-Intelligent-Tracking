const API_URL = 'http://127.0.0.1:8000/api';

/**
 * Fetch personalized recommendations for a user.
 * Pass `productIdViewed` if the user is currently viewing a product (context-aware mode).
 */
export const getRecommendations = async (userId, productIdViewed = null) => {
  try {
    const payload = {
      user_id: userId,
      n_recommendations: 20,
    };

    if (productIdViewed) {
      payload.product_id_viewed = productIdViewed;
    }

    const response = await fetch(`${API_URL}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error(`Recommend failed: ${response.status}`);

    const data = await response.json();
    return {
      recommendations: data.recommendations || [],
      strategy: data.strategy || 'unknown',
    };
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    return { recommendations: [], strategy: 'error' };
  }
};

/**
 * Search for products by keyword with TF-IDF relevance scoring.
 */
export const searchProducts = async (query) => {
  try {
    const response = await fetch(
      `${API_URL}/search?query=${encodeURIComponent(query)}`
    );
    if (!response.ok) throw new Error(`Search failed: ${response.status}`);

    const data = await response.json();
    return data.results || [];
  } catch (error) {
    console.error('Error searching products:', error);
    return [];
  }
};

/**
 * Log a user–product interaction to the backend.
 * Types: 'view', 'click', 'add_to_cart', 'purchase'
 */
export const logInteraction = async (userId, productId, action = 'click') => {
  try {
    await fetch(`${API_URL}/interactions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: String(userId),
        product_id: String(productId),
        interaction_type: action,
      }),
    });
  } catch (error) {
    console.error('Error logging interaction:', error);
  }
};

/**
 * Fetch a single product by ASIN.
 */
export const getProduct = async (asin) => {
  try {
    const response = await fetch(`${API_URL}/products/${asin}`);
    if (!response.ok) throw new Error(`Product fetch failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching product:', error);
    return null;
  }
};