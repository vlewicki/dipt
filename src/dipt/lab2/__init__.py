"""Пакет dipt.lab2 — обезличивание персональных данных.

Экспортирует публичную функцию anon.
"""

from dipt.lab2.main import main
from .anon import anon

__all__ = ["anon"]