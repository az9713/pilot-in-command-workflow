"""
REST API module for avatar pipeline.

Provides FastAPI-based REST API for pipeline execution, job management,
and component operations.
"""

from .main import app, create_app

__all__ = ["app", "create_app"]
