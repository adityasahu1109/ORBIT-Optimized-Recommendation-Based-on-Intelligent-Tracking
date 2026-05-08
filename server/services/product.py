"""
Product catalog service.
Thin wrapper around PopularityEngine for product data access.
"""

from server.engines.popularity import PopularityEngine


class ProductService:
    def __init__(self, popularity_engine: PopularityEngine):
        self.engine = popularity_engine

    def get_product(self, asin: str) -> dict | None:
        """Get a single product by ASIN."""
        return self.engine.get_product_info(asin)

    def get_product_category(self, asin: str) -> str | None:
        """Get the category name for a product."""
        return self.engine.get_product_category(asin)
