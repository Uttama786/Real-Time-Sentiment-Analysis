"""API package initialization"""
from api.routes import router
from api.middleware import setup_middleware

__all__ = ['router', 'setup_middleware']
