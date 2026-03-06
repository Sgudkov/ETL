"""
Модуль для определения базового класса SQLAlchemy.

Этот модуль импортирует `declarative_base` из `sqlalchemy.ext.declarative`
и создает экземпляр `Base`, который будет служить основой для всех
декларативных моделей SQLAlchemy.
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
