"""
Abstract base class for all recommendation engines.
Ensures a consistent interface across Popularity, Collaborative, Content, and Search engines.
"""

from abc import ABC, abstractmethod


class BaseEngine(ABC):
    """All engines must implement these methods."""

    @abstractmethod
    def initialize(self) -> None:
        """Load data, models, or precompute whatever the engine needs."""
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return a human-readable engine name for logging."""
        ...
