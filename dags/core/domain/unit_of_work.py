"""Абстрактный класс для Unit of Work.

Unit of Work — это шаблон проектирования, который управляет транзакциями,
группируя набор операций в одну рабочую единицу.
"""

from abc import abstractmethod
from contextlib import AbstractContextManager

from core.domain.repositories import IBaseRepository


class IUnitOfWork(AbstractContextManager):
    """Реализация Unit of Work определяет репозитории для различных доменных сущностей."""

    repo: IBaseRepository

    @abstractmethod
    def commit(self):
        """Сохраняет изменения."""
        pass

    @abstractmethod
    def rollback(self):
        """Откатывает изменения."""
        pass
