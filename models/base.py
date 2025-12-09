"""Declarative Base única para todos los modelos."""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

__all__ = ["Base"]
