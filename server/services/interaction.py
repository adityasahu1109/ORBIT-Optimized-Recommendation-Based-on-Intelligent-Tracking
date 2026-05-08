"""
Interaction logging and retrieval service.
Handles writing interactions to the DB and fetching user history.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc

from server.db.models import Interaction
from server.config import USER_HISTORY_LIMIT


class InteractionService:
    @staticmethod
    def log_interaction(
        db: Session, user_id: str, product_id: str, interaction_type: str
    ) -> Interaction:
        """Log a new user-product interaction to the database."""
        new_interaction = Interaction(
            user_id=user_id,
            product_id=product_id,
            interaction_type=interaction_type,
        )
        db.add(new_interaction)
        db.commit()
        db.refresh(new_interaction)
        return new_interaction

    @staticmethod
    def get_recent_interactions(
        db: Session, user_id: str, limit: int = USER_HISTORY_LIMIT
    ) -> list[Interaction]:
        """
        Fetch the N most recent interactions for a user,
        ordered by timestamp descending (newest first).
        """
        return (
            db.query(Interaction)
            .filter(Interaction.user_id == user_id)
            .order_by(desc(Interaction.timestamp))
            .limit(limit)
            .all()
        )

    @staticmethod
    def has_history(db: Session, user_id: str) -> bool:
        """Check if a user has any interaction history."""
        return (
            db.query(Interaction)
            .filter(Interaction.user_id == user_id)
            .first()
        ) is not None
