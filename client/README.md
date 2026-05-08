# ORBIT Frontend — React + Vite + Tailwind CSS

The `client/` directory contains the React SPA for ORBIT. It provides product browsing, search, a shopping cart, and a **User Simulation Panel** for testing recommendation strategies in real time.

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI framework |
| Vite | 7.x | Dev server + bundler |
| Tailwind CSS | 4.x | Utility-first styling |
| React Router | 6.x | Client-side routing |
| Lucide React | — | Icons |

---

## Component Architecture

```mermaid
graph TD
    BR["BrowserRouter"] --> UP["UserProvider"]
    UP --> App["App"]

    App --> Nav["Navbar<br/>Search + User Simulator + Cart"]
    App --> Routes["Routes"]
    App --> Foot["Footer"]

    Routes --> Home["/ → Home"]
    Routes --> PDP["/product/:asin → ProductDetails"]
    Routes --> SR["/search → SearchResults"]
    Routes --> Cart["/cart → Cart"]

    Home --> PG["ProductGrid"] --> PC["ProductCard"]
    SR --> PC
    PDP --> PG
```

### State Flow

```mermaid
flowchart LR
    subgraph UserContext
        UID["userId"]
        CART["cartItems"]
    end

    UID -->|persisted| LS1["localStorage"]
    CART -->|persisted| LS2["localStorage"]

    Nav["Navbar"] -->|setUserId| UID
    PDP["ProductDetails"] -->|addToCart| CART
    CartPage["Cart"] -->|removeFromCart / clearCart| CART
    UID -->|read by| Home & PDP
```

### API Integration

```mermaid
sequenceDiagram
    participant UI as React
    participant API as api.js
    participant BE as FastAPI

    UI->>API: getRecommendations(userId)
    API->>BE: POST /api/recommend
    BE-->>UI: recommendations[]

    UI->>API: searchProducts(query)
    API->>BE: GET /api/search
    BE-->>UI: results[]

    UI->>API: logInteraction(userId, asin, type)
    API->>BE: POST /api/interactions
```

---

## Key Features

- **User Simulator**: Switch between users (1001–1100) or cold user (9999) from the navbar
- **Strategy Badges**: 🔥 Trending, ✨ For You, 🔗 Similar, 📈 Popular on each card
- **Cold Start UI**: Shows "Trending Products" banner when user has no history
- **Skeleton Loading**: Animated placeholders during API calls

---

## Running

```bash
cd client
npm install       # Install dependencies
npm run dev       # Dev server at http://localhost:5173
npm run build     # Production build to dist/
```

> The backend must be running on `http://127.0.0.1:8000` for API calls to work.
