# ORBIT - Optimized Recommendation-Based Intelligent Tracking System

ORBIT is an **Optimized Recommendation-Based Intelligent Tracking system** that delivers personalized product recommendations using a hybrid approach combining SVD Collaborative Filtering, TF-IDF Content Similarity, Bayesian Popularity Ranking, and real-time user interaction tracking — all built on a train-once, load-from-disk architecture.

## System Architecture

ORBIT implements a **layered web application architecture** with strict separation of concerns:

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Client Layer** | React, Vite, Tailwind CSS | User interface, user simulation, search, localStorage cart |
| **API Layer** | FastAPI, Pydantic, Uvicorn | Thin request routing, schema validation |
| **Service Layer** | Python classes | Orchestration logic, profile building, interaction logging |
| **Engine Layer** | scikit-learn, Surprise (SVD) | ML model inference (train-once, load from disk) |
| **Data Layer** | SQLAlchemy, SQLite, Pandas | Interaction persistence, product catalog |

### Architecture Overview

```mermaid
graph TB
    subgraph ClientTier["Client Tier (React SPA)"]
        Browser["Web Browser"]
        
        subgraph ReactApp["React Application"]
            AppJsx["App.jsx<br/>Routes Component"]
            
            subgraph Pages["Pages (client/src/pages/)"]
                HomePage["Home.jsx"]
                ProductDetailsPage["ProductDetails.jsx"]
                SearchResultsPage["SearchResults.jsx"]
                CartPage["Cart.jsx"]
            end
            
            subgraph Components["Components (client/src/components/)"]
                NavbarComp["Navbar.jsx<br/>Search + User Simulator"]
                ProductCardComp["ProductCard.jsx<br/>Strategy Badges"]
                ProductGridComp["ProductGrid.jsx<br/>Engine Indicator"]
                LoadingComp["LoadingSkeleton.jsx"]
                FooterComp["Footer.jsx"]
            end
            
            UserCtx["context/UserContext.jsx<br/>userId, cartItems<br/>setUserId(), addToCart()"]
            
            ApiService["services/api.js<br/>getRecommendations()<br/>logInteraction()<br/>searchProducts()<br/>getProduct()"]
        end
    end
    
    subgraph BackendTier["Backend Tier (FastAPI)"]
        MainPy["server/main.py<br/>FastAPI app factory<br/>Lifespan handler"]
        
        subgraph APILayer["API Layer (server/api/)"]
            subgraph Endpoints["HTTP Endpoints"]
                RecommendEP["POST /api/recommend<br/>get_recommendations()"]
                InteractionEP["POST /api/interactions<br/>log_interaction()"]
                SearchEP["GET /api/search<br/>search_products()"]
                ProductEP["GET /api/products/:asin<br/>get_product()"]
                HealthEP["GET /<br/>health_check()"]
            end
            
            SchemasPy["server/api/schemas.py<br/>Pydantic Models<br/>InteractionCreate, RecommendationRequest"]
        end
        
        subgraph ServiceLayer["Service Layer (server/services/)"]
            RecService["recommendation.py<br/>RecommendationService<br/>get_recommendations()<br/>_build_category_profile()<br/>_enforce_diversity()"]
            IntService["interaction.py<br/>InteractionService<br/>log_interaction()<br/>get_recent_interactions()"]
            ProdService["product.py<br/>ProductService<br/>get_product()"]
        end
        
        subgraph EngineLayer["Engine Layer (server/engines/)"]
            PopEngine["popularity.py<br/>PopularityEngine<br/>Bayesian scoring"]
            CollabEngine["collaborative.py<br/>CollaborativeEngine<br/>SVD predictions"]
            ContentEngine["content.py<br/>ContentEngine<br/>TF-IDF similarity"]
            SearchEngine["search.py<br/>SearchEngine<br/>TF-IDF relevance search"]
        end
        
        subgraph DBLayer["Database Layer (server/db/)"]
            EnginePy["engine.py<br/>SessionLocal, get_db()<br/>init_db()"]
            ModelsPy["models.py<br/>Interaction ORM model"]
        end
    end
    
    subgraph DataTier["Data & Model Tier"]
        subgraph DataSources["Data Sources"]
            SQLiteDB["data/orbit.db<br/>interactions table"]
            ProductCSV["data/cleaned_products.csv<br/>~156K products"]
            RawCSV["data/amazon_products.csv<br/>~2.2M products"]
        end
        
        subgraph ModelFiles["Pre-trained Models"]
            SVDModel["models/svd_model.pkl<br/>Surprise SVD model"]
            TFIDFBundle["models/tfidf_bundle.pkl<br/>TF-IDF vectorizer + sparse matrix"]
        end
    end
    
    Browser --> AppJsx
    AppJsx --> Pages
    AppJsx --> Components
    Pages --> UserCtx
    Pages --> ApiService
    
    ApiService -->|"HTTP/JSON"| MainPy
    
    MainPy --> APILayer
    Endpoints --> SchemasPy
    
    RecommendEP --> RecService
    InteractionEP --> IntService
    ProductEP --> ProdService
    
    RecService --> PopEngine
    RecService --> CollabEngine
    RecService --> ContentEngine
    IntService --> EnginePy
    
    SearchEP --> SearchEngine
    ContentEngine -.->|"shares vectorizer"| SearchEngine
    
    EnginePy --> SQLiteDB
    PopEngine --> ProductCSV
    ContentEngine --> TFIDFBundle
    CollabEngine --> SVDModel
    CollabEngine --> EnginePy
```

## Core Components

### 1. Recommendation Engines

#### PopularityEngine

Handles cold-start scenarios using a **Bayesian-averaged** weighted scoring formula:

```python
bayesian_stars = (R * v + C * m) / (v + m)    # Bayesian average (prevents low-vote outliers)

popularity_score = bayesian_stars * 2.0
                 + log(reviews + 1) * 0.5       # Log-scaled review volume
                 + log(boughtInLastMonth + 1) * 0.3   # Trending signal
                 + (2.0 if isBestSeller)
```

Where `C` = global mean star rating, `m` = minimum votes threshold (25), `R` = product rating, `v` = review count.

#### ContentEngine

Provides content-based filtering using **sparse TF-IDF vectorization** and cosine similarity on enriched product tags:
- Tags combine: `title + category + price_bucket + quality_bucket + bestseller_token`
- All operations on scipy sparse matrices — **no PyTorch needed** (~900MB RAM saved vs. old system)
- TF-IDF bundle is pre-built by `scripts/train_model.py` and loaded from disk on startup

#### CollaborativeEngine

Uses **SVD (Singular Value Decomposition)** via the Surprise library for collaborative filtering with key improvements:
- **Temporal decay**: interactions lose half their weight every 14 days (`exp(-0.693 * days / halflife)`)
- **Additive aggregation**: repeated views/clicks accumulate signal (old system used `.max()` which lost granularity)
- **[1.0, 5.0] normalization** for proper SVD training scale
- Model is trained once via `scripts/train_model.py` and loaded from disk — no runtime retraining

#### SearchEngine

Smart search using TF-IDF relevance scoring — replaces the old substring-matching approach:
- **Shares** the ContentEngine's TF-IDF vectorizer (no duplicate data in memory)
- Query is vectorized → cosine similarity against all products → hybrid ranking
- Score formula: `relevance * 0.7 + quality * 0.3`
- Minimum similarity threshold (0.02) filters out garbage results
- **Regex-safe**: no `str.contains()`, immune to special characters like `C++`, `(`, etc.

### 2. API Endpoints

The FastAPI backend exposes five endpoints through `server/api/routes.py`:

- **POST /api/recommend** — Generates personalized, context-aware, or cold-start recommendations
- **POST /api/interactions** — Logs user behavior (view, click, add_to_cart, purchase)
- **GET /api/search** — Executes TF-IDF relevance search queries
- **GET /api/products/{asin}** — Retrieves a single product by ASIN
- **GET /** — Health check endpoint

### 3. Recommendation Strategies

ORBIT uses **three recommendation strategies** selected automatically based on context:

1. **Cold Start Mode**: New user with no history → returns popularity-ranked products with diversity enforcement (min 3 categories)
2. **Personalized Mode**: User with history → builds decayed category profile from last 20 interactions, combines SVD scores with bounded category boost, enforces diversity
3. **Context-Aware Mode**: User viewing a specific product → returns TF-IDF content-similar products

**Key stability fix**: A single product view contributes ~1% to the recommendation score (was 33-75% in the old system due to flat +1.5 category boost).

## Data Flow and User Journeys

### Overall Data Flow

```mermaid
graph LR
    User["User Interaction"] --> React["React Frontend"]
    React -->|"HTTP/JSON"| API["FastAPI Backend"]
    API --> DB[("SQLite Database<br/>orbit.db")]
    API --> Services["Service Layer"]
    Services --> Engines["ML Engines"]
    Engines --> Models["Pre-trained Models<br/>svd_model.pkl<br/>tfidf_bundle.pkl"]
    Engines --> Catalog["Product Catalog<br/>cleaned_products.csv"]
    Services --> API
    API -->|"JSON Response"| React
```

### Recommendation Request Flow

```mermaid
sequenceDiagram
    participant Client as React Client
    participant API as FastAPI Backend
    participant RecSvc as RecommendationService
    participant IntSvc as InteractionService
    participant DB as SQLite Database
    participant PopEngine as Popularity Engine
    participant ContentEngine as Content Engine
    participant CollabEngine as Collaborative Engine
    
    Client->>API: POST /api/recommend {user_id, product_id_viewed?, n_recommendations}
    API->>RecSvc: get_recommendations(db, user_id, product_id_viewed, n)
    
    alt Context-Aware Mode (product_id_viewed is set)
        RecSvc->>ContentEngine: find_similar_products(product_asin, k)
        ContentEngine-->>RecSvc: Similar products with cosine similarity scores
        RecSvc-->>Client: Context-aware recommendations
    else Cold Start Mode (no user history)
        RecSvc->>IntSvc: has_history(db, user_id)
        IntSvc-->>RecSvc: false
        RecSvc->>PopEngine: get_top_products(k=30)
        PopEngine-->>RecSvc: Bayesian-ranked products
        RecSvc->>RecSvc: _enforce_diversity(min 3 categories)
        RecSvc-->>Client: Cold-start recommendations
    else Personalized Mode (user has history)
        RecSvc->>IntSvc: get_recent_interactions(db, user_id, limit=20)
        IntSvc->>DB: Query last 20 interactions
        DB-->>IntSvc: Interaction records with timestamps
        IntSvc-->>RecSvc: Recent interactions
        RecSvc->>RecSvc: _build_category_profile() with temporal decay
        RecSvc->>PopEngine: get_top_products(k=30) + get_top_in_category(top 3 cats)
        PopEngine-->>RecSvc: Candidate products
        RecSvc->>CollabEngine: predict_score(user_id, product_id) for each candidate
        CollabEngine-->>RecSvc: SVD affinity scores (1.0-5.0)
        RecSvc->>RecSvc: Score = SVD * 0.7 + category_boost * 0.3
        RecSvc->>RecSvc: _enforce_diversity(min 3 categories)
        RecSvc-->>Client: Personalized recommendations
    end
```

### Engine Initialization Flow (Server Startup)

```mermaid
graph LR
    Startup["uvicorn server.main:app"] --> InitDB["init_db()<br/>Create SQLite tables"]
    InitDB --> LoadPop["PopularityEngine()<br/>Load CSV + compute Bayesian scores"]
    LoadPop --> LoadCollab["CollaborativeEngine()<br/>Load SVD from models/svd_model.pkl"]
    LoadCollab --> LoadContent["ContentEngine()<br/>Load TF-IDF from models/tfidf_bundle.pkl"]
    LoadContent --> LoadSearch["SearchEngine(content_engine)<br/>Share TF-IDF + precompute quality"]
    LoadSearch --> WireServices["Wire up services<br/>RecommendationService<br/>InteractionService<br/>ProductService"]
    WireServices --> InjectRoutes["Inject services into API routes"]
    InjectRoutes --> Ready["Server Ready<br/>No training at startup"]
```

### Training Pipeline (One-time Setup)

```mermaid
graph LR
    RawCSV["data/amazon_products.csv<br/>2.2M products"] -->|"scripts/setup_data.py"| CleanCSV["data/cleaned_products.csv<br/>~156K stratified sample"]
    CleanCSV -->|"scripts/seed_interactions.py"| DB[("data/orbit.db<br/>~2K mock interactions")]
    CleanCSV -->|"scripts/train_model.py"| TFIDF["models/tfidf_bundle.pkl<br/>TF-IDF vectorizer + sparse matrix"]
    DB -->|"scripts/train_model.py"| SVD["models/svd_model.pkl<br/>Surprise SVD model"]
```

## Key Features

- **Train-Once Architecture**: Models are trained offline and loaded from disk — no runtime retraining on every startup
- **Real-time Interaction Tracking**: Logs user behavior (view, click, add_to_cart, purchase) to SQLite for profile building
- **Hybrid Recommendation Strategy**: Combines SVD collaborative filtering, TF-IDF content similarity, and Bayesian popularity ranking
- **Temporal Decay**: Recent interactions matter more — half-life of 14 days prevents stale history from dominating
- **Diversity Enforcement**: At least 3 distinct categories in top-N results to prevent filter bubbles
- **Smart Search**: TF-IDF relevance scoring replaces naive substring matching — immune to regex injection
- **User Simulation Panel**: Switch between users in real-time from the navbar for testing/debugging
- **Model Caching**: Pre-computes and caches TF-IDF matrices and SVD models for instant startup

## Frontend Integration

The React application follows a component-based architecture with centralized state management via `UserContext`:

```mermaid
graph TB
    subgraph Providers["Provider Layer"]
        BrowserRouter["BrowserRouter"]
        UserProvider["UserProvider<br/>(UserContext.jsx)<br/>userId, cartItems, setUserId()"]
    end
    
    BrowserRouter --> UserProvider
    UserProvider --> AppComponent
    
    AppComponent["App Component<br/>(App.jsx)"]
    
    NavbarSticky["Navbar<br/>(Sticky Top)<br/>Search bar + User Simulator dropdown + Cart badge"]
    MainContent["main element<br/>(flex-grow)"]
    FooterFixed["Footer<br/>(Fixed Bottom)"]
    
    Routes["Routes Component"]
    
    RouteHome["Route: /<br/>element: Home<br/>Strategy-aware hero banner"]
    RouteProduct["Route: /product/:asin<br/>element: ProductDetails<br/>Similar products via ContentEngine"]
    RouteSearch["Route: /search<br/>element: SearchResults<br/>TF-IDF ranked results"]
    RouteCart["Route: /cart<br/>element: Cart<br/>Purchase interaction logging"]
    
    AppComponent --> NavbarSticky
    AppComponent --> MainContent
    AppComponent --> FooterFixed
    
    MainContent --> Routes
    Routes --> RouteHome
    Routes --> RouteProduct
    Routes --> RouteSearch
    Routes --> RouteCart
```

The frontend communicates with the backend via HTTP/JSON API calls through the `services/api.js` module. User state (userId + cart) is managed via React Context and persisted to `localStorage`.

## Setup & Running

### Prerequisites
- Python 3.10+ (with conda or venv)
- Node.js 18+ and npm
- The raw Amazon dataset (`data/amazon_products.csv`)

### Installation

```bash
git clone https://github.com/adityasahu1109/ORBIT-Optimized-Recommendation-Based-on-Intelligent-Tracking.git
cd ORBIT-Optimized-Recommendation-Based-on-Intelligent-Tracking

# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd client && npm install && cd ..
```

### Running the Application

The server **automatically handles first-run setup**. If it detects missing data or models, it will:
1. Clean and sample from the raw 2.2M product CSV → ~156K products
2. Seed mock user interactions (100 users, ~2K interactions)
3. Train SVD + build TF-IDF bundle and save to `models/`

Just start the server — everything is handled:

```bash
# Terminal 1: Start the FastAPI backend (auto-setup on first run)
uvicorn server.main:app --reload

# Terminal 2: Start the React frontend
cd client && npm run dev
```

Open **http://localhost:5173** in your browser. Interactive API docs at **http://localhost:8000/docs**.

> **Note**: First startup takes 30-60 seconds for auto-setup. Subsequent starts load instantly from disk.

### Manual Scripts (Optional)

If you want to re-run individual steps manually:

```bash
python -m scripts.setup_data           # Re-clean + resample from raw CSV
python -m scripts.seed_interactions    # Regenerate mock interaction data
python -m scripts.train_model          # Retrain SVD + rebuild TF-IDF bundle
```

## Notes

- The system uses SQLite for persistence with SQLAlchemy ORM — database stored at `data/orbit.db`
- Product catalog is stored in `data/cleaned_products.csv` (~156K stratified sample from 2.2M raw products)
- Pre-trained models are cached in the `models/` directory — only re-run `scripts/train_model.py` to refresh
- First-run auto-setup detects missing files and runs the full pipeline automatically
- CORS is configured for development with React on localhost:5173
- The SearchEngine shares the ContentEngine's TF-IDF vectorizer to avoid duplicate data in memory
- The system supports cold-start, personalized, and context-aware recommendation modes
- Category boosting is proportional to decayed profile weight — a single view contributes ~1% (not a flat +1.5)
- All configuration (hyperparameters, paths, weights) lives in `server/config.py` as a single source of truth

