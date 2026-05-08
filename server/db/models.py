"""
ORM models for the ORBIT database.
"""

from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime, timezone

from server.db.engine import Base


class Interaction(Base):
    """
    Records a single user–product interaction.
    Types: 'view', 'click', 'add_to_cart', 'purchase'
    """
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    product_id = Column(String, nullable=False, index=True)
    interaction_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Composite index for fast "get recent interactions for user" queries
    __table_args__ = (
        Index("ix_user_timestamp", "user_id", "timestamp"),
    )

    def __repr__(self):
        return (
            f"<Interaction(user={self.user_id}, product={self.product_id}, "
            f"type={self.interaction_type}, time={self.timestamp})>"
        )
