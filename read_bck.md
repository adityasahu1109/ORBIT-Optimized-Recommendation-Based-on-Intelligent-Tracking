# ORBIT - Optimized Recommendation-Based Intelligent Tracking system

ORBIT is an **Optimized Recommendation-Based Intelligent Tracking system** that delivers personalized product recommendations using a hybrid approach combining multiple ML algorithms and real-time user interaction tracking.  

## System Architecture

ORBIT implements a **three-tier web application architecture** with clear separation of concerns:

| Tier | Technology | Purpose |
|------|------------|---------|
| **Client Layer** | React, Vite, Tailwind CSS | User interface, navigation, localStorage cart |
| **API Layer** | FastAPI, Pydantic, SQLAlchemy | Request validation, engine orchestration, interaction logging |
| **Engine/Data Layer** | Scikit-learn, PyTorch, SQLite | ML model inference, data persistence, product catalog |

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
                NavbarComp["Navbar.jsx"]
                FooterComp["Footer.jsx"]
                ProductCardComp["ProductCard.jsx"]
                RecSectionComp["RecommendationSection.jsx"]
            end
            
            ApiService["services/api.js<br/>getRecommendations()<br/>logInteraction()<br/>searchProducts()"]
        end
    end
    
    subgraph APITier["API Tier (FastAPI)"]
        MainPy["app/main.py<br/>FastAPI instance"]
        
        subgraph Endpoints["HTTP Endpoints"]
            LogInteractionEP["POST /log-interaction<br/>log_user_interaction()"]
            RecommendEP["POST /recommend<br/>get_recommendations()"]
            SearchEP["GET /search<br/>search_products()"]
            HealthEP["GET /<br/>health_check()"]
        end
        
        SchemasPy["app/schemas.py<br/>Pydantic Models"]
        
        DatabasePy["database.py<br/>get_db()<br/>Interaction model"]
    end
    
    subgraph EngineDataTier["Engine & Data Tier"]
        subgraph Engines["ML Engines"]
            PopEngine["app/popularity.py<br/>PopularityRecommender"]
            ContentEngine["app/content_engine.py<br/>ContentEngine"]
            CollabEngine["app/collaborative_engine.py<br/>CollaborativeEngine"]
        end
        
        subgraph DataSources["Data Sources"]
            SQLiteDB["data/orbit.db<br/>interactions table"]
            ProductCSV["data/cleaned_products.csv<br/>Product catalog"]
            ModelCache["models/<br/>content_engine.pkl<br/>collab_model.pkl"]
        end
    end
    
    Browser --> AppJsx
    AppJsx --> Pages
    AppJsx --> Components
    Pages --> ApiService
    
    ApiService -->|"HTTP/JSON"| MainPy
    
    MainPy --> Endpoints
    Endpoints --> SchemasPy
    LogInteractionEP --> DatabasePy
    RecommendEP --> DatabasePy
    
    MainPy -->|"engines dict"| PopEngine
    MainPy -->|"engines dict"| ContentEngine
    MainPy -->|"engines dict"| CollabEngine
    
    DatabasePy --> SQLiteDB
    PopEngine --> ProductCSV
    ContentEngine --> ProductCSV
    ContentEngine --> ModelCache
    CollabEngine --> SQLiteDB
    CollabEngine --> ModelCache
```

## Core Components

### 1. Recommendation Engines

#### PopularityRecommender

Handles cold-start scenarios using a weighted scoring formula:

```python
popularity_score = (stars × 2.0) + (log(reviews + 1) × 0.5) + (boughtInLastMonth × 0.01) + (isBestSeller × 2.0)
```

#### ContentEngine

Provides content-based filtering using TF-IDF vectorization and cosine similarity with GPU acceleration:

#### CollaborativeEngine

Uses SVD (Singular Value Decomposition) for collaborative filtering based on user interaction history.

### 2. API Endpoints

The FastAPI backend exposes four main endpoints:

- **POST /log-interaction** - Tracks user behavior (view, click, add_to_cart, purchase)
- **POST /recommend** - Generates personalized or context-aware recommendations
- **GET /search** - Executes product search queries
- **GET /** - Health check endpoint

### 3. Recommendation Strategies

ORBIT uses **context-aware recommendation logic** with two main scenarios:

1. **Context-Aware Mode**: When viewing a specific product, returns similar items using ContentEngine
2. **Personalized Feed Mode**: For homepage, combines popularity scores with collaborative filtering and category boosting

## Data Flow and User Journeys

### Overall Data Flow

```mermaid
graph LR
    User[User Interaction] --> API[FastAPI Backend]
    API --> DB[(SQLite Database)]
    API --> Engines[ML Engines]
    Engines --> Models[Pre-trained Models]
    Engines --> Catalog[Product Catalog]
    API --> Response[Recommendation Response]
```

### Recommendation Request Flow

```mermaid
sequenceDiagram
    participant Client as React Client
    participant API as FastAPI Backend
    participant DB as SQLite Database
    participant PopEngine as Popularity Engine
    participant ContentEngine as Content Engine
    participant CollabEngine as Collaborative Engine
    
    Client->>API: POST /recommend {user_id, product_id_viewed?}
    
    alt Context-Aware Mode
        API->>ContentEngine: find_similar_products(product_id)
        ContentEngine-->>API: Similar products with scores
        API-->>Client: Context-aware recommendations
    else Personalized Feed Mode
        API->>DB: Query last interaction
        DB-->>API: Last viewed product/category
        API->>PopEngine: get_recommendations(k=50)
        PopEngine-->>API: Top popular products
        API->>CollabEngine: predict_score(user_id, product_id)
        CollabEngine-->>API: SVD scores
        API->>API: Apply category boosting + sort
        API-->>Client: Personalized recommendations
    end
```

### Engine Initialization Flow

```mermaid
graph LR
    Startup["Application Startup"] --> LoadPop["Load Popularity Engine"]
    LoadPop --> LoadContent["Load Content Engine"]
    LoadContent --> LoadCollab["Load Collaborative Engine"]
    LoadCollab --> Ready["API Ready"]
    
    LoadContent --> CheckCache{"Cache exists?"}
    CheckCache -->|Yes| LoadCache["Load from models/content_engine.pkl"]
    CheckCache -->|No| BuildNew["Build TF-IDF from scratch"]
    BuildNew --> SaveCache["Save to cache"]
    LoadCache --> Ready
    SaveCache --> Ready
```

## Key Features

- **Real-time Interaction Tracking**: Logs user behavior to improve recommendations
- **Hybrid Recommendation Strategy**: Combines multiple algorithms for optimal results
- **Category Boosting**: Enhances recommendations based on user's recent interests
- **GPU Acceleration**: Uses PyTorch for faster similarity computations
- **Model Caching**: Pre-computes and caches expensive operations for fast startup

## Frontend Integration

The React application structure follows a component-based architecture:

```mermaid
graph TB
    AppComponent["App Component<br/>(App.jsx)"]
    
    NavbarSticky["Navbar<br/>(Sticky Top)"]
    MainContent["main element<br/>(flex-grow)"]
    FooterFixed["Footer<br/>(Fixed Bottom)"]
    
    Routes["Routes Component"]
    
    RouteHome["Route: /<br/>element: Home"]
    RouteProduct["Route: /product/:asin<br/>element: ProductDetails"]
    RouteSearch["Route: /search<br/>element: SearchResults"]
    RouteCart["Route: /cart<br/>element: Cart"]
    
    AppComponent --> NavbarSticky
    AppComponent --> MainContent
    AppComponent --> FooterFixed
    
    MainContent --> Routes
    Routes --> RouteHome
    Routes --> RouteProduct
    Routes --> RouteSearch
    Routes --> RouteCart
```

The frontend communicates with the backend via HTTP/JSON API calls through the `services/api.js` module.

## Notes

- The system uses SQLite for persistence with SQLAlchemy ORM
- Product catalog is stored in `data/cleaned_products.csv`
- Models are cached in the `models/` directory for fast initialization
- CORS is configured for development with React on localhost:5173
- The ContentEngine includes optimization to load pre-computed TF-IDF matrices from cache
- The system supports both context-aware and personalized recommendation modes
- Category boosting is applied based on user's last interaction to improve relevance
