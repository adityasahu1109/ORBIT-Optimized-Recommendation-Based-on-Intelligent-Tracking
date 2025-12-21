import streamlit as st
import requests
import time

# Configuration
API_URL = "http://127.0.0.1:8000"

# Page Setup
st.set_page_config(page_title="ORBIT Recommender", layout="wide")
st.title("🪐 ORBIT: AI Recommendation System")

# --- STATE MANAGEMENT ---
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# --- HELPER FUNCTIONS ---

def get_valid_image(url, title):
    """
    If URL is missing/broken, return a placeholder with the product name text.
    """
    if not url or str(url) == "0" or not str(url).startswith("http"):
        # Create a URL-safe short title
        safe_title = title.split(",")[0].strip()[:20] 
        safe_title = safe_title.replace(" ", "+")
        return f"https://placehold.co/400x300/EEE/31343C?text={safe_title}"
    return url

def log_interaction(user_id, product_id, action="click"):
    """
    Log interaction and wait briefly to ensure DB update before reload.
    """
    try:
        payload = {
            "user_id": str(user_id),
            "product_id": str(product_id),
            "interaction_type": action
        }
        requests.post(f"{API_URL}/log-interaction", json=payload)
        time.sleep(0.05) # Tiny delay to ensure backend DB commits
    except:
        pass 

def get_recommendations(user_id, product_viewed=None):
    payload = {"user_id": user_id, "n_recommendations": 8}
    if product_viewed:
        payload["product_id_viewed"] = product_viewed
    
    try:
        response = requests.post(f"{API_URL}/recommend", json=payload)
        if response.status_code == 200:
            return response.json().get("recommendations", [])
        return []
    except:
        return []

def search_products(query):
    try:
        response = requests.get(f"{API_URL}/search", params={"query": query})
        if response.status_code == 200:
            return response.json().get("results", [])
        return []
    except:
        return []

# --- SIDEBAR NAV ---
st.sidebar.header("Navigation")
# Using radio button ensures we stay on the correct page after a rerun
page = st.sidebar.radio("Go to", ["Home / Feed", "Search"])

st.sidebar.divider()
st.sidebar.header("User Simulation")
user_id = st.sidebar.text_input("User ID", value="1001")
st.sidebar.info(f"Current Persona: User {user_id}")

if st.sidebar.button("Reset / New User"):
    user_id = "9999"
    st.sidebar.success("Switched to Cold User (9999)")

# --- GLOBAL DETAIL VIEW ---
# This sits above the main content so it pushes everything down
if 'viewed_product' in st.session_state:
    product = st.session_state['viewed_product']
    
    with st.container():
        st.info(f"👀 You are currently viewing: **{product['title']}**")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            img_url = get_valid_image(product.get('imgUrl'), product['title'])
            st.image(img_url, width=250)
            st.write(f"**Price:** ${product.get('price', 'N/A')}")
            
            if st.button("Close Details", type="primary"):
                del st.session_state['viewed_product']
                st.rerun()

        with col2:
            st.subheader("People who viewed this also liked:")
            similar_items = get_recommendations(user_id, product_viewed=product['asin'])
            
            if similar_items:
                sim_cols = st.columns(4)
                for idx, s_item in enumerate(similar_items):
                    with sim_cols[idx % 4]:
                        s_img = get_valid_image(s_item.get('imgUrl'), s_item['title'])
                        st.image(s_img, use_container_width=True)
                        st.caption(f"{s_item['title'][:40]}...")
    st.divider()

# --- PAGE LOGIC ---

if page == "Home / Feed":
    st.subheader(f"Top Picks for You (User {user_id})")
    
    # Check if we should clear search state when coming home (optional)
    # st.session_state.search_query = "" 
    
    recs = get_recommendations(user_id)
    
    if recs:
        cols = st.columns(4)
        for idx, item in enumerate(recs):
            with cols[idx % 4]:
                img_url = get_valid_image(item.get('imgUrl'), item['title'])
                st.image(img_url, use_container_width=True)
                
                st.write(f"**{item['title'][:40]}...**")
                if "Because" in item['reason']:
                    st.success(item['reason']) # Highlight the Real-Time Boost
                else:
                    st.caption(item['reason'])
                
                if st.button(f"View Details", key=f"btn_{item['asin']}"):
                    log_interaction(user_id, item['asin'], "click")
                    st.session_state['viewed_product'] = item
                    st.rerun()

elif page == "Search":
    st.subheader("Search Products")
    
    # Callback to update results immediately when Enter is pressed
    def run_search():
        st.session_state.search_results = search_products(st.session_state.search_query)

    # FIX: Explicitly set 'value' to ensure text persists on reload
    query = st.text_input(
        "Enter keyword (e.g., 'sony', 'printer')", 
        value=st.session_state.search_query,  # <--- THIS IS THE FIX
        key="search_query", 
        on_change=run_search
    )

    # If results exist, show them
    if st.session_state.search_results:
        st.success(f"Found {len(st.session_state.search_results)} results")
        
        for item in st.session_state.search_results:
            with st.expander(f"{item['title']} - ${item.get('price', '0.00')}"):
                col_a, col_b = st.columns([1, 4])
                with col_a:
                    img_url = get_valid_image(item.get('imgUrl'), item['title'])
                    st.image(img_url, width=100)
                with col_b:
                    st.write(f"**Category:** {item['categoryName']}")
                    st.write(f"**Stars:** {item['stars']} ({item['reviews']} reviews)")
                    
                    if st.button("View Similar & Details", key=f"search_{item['asin']}"):
                        log_interaction(user_id, item['asin'], "click")
                        st.session_state['viewed_product'] = item
                        st.rerun()