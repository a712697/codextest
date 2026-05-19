"""Dependency-free core for supermarket product/inventory rules."""

from .db import connect, initialize_database
from .services import SupermarketService

__all__ = ["connect", "initialize_database", "SupermarketService"]
