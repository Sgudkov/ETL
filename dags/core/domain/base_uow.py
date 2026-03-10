"""Абстрактный класс для Unit of Work.

Unit of Work — это шаблон проектирования, который управляет транзакциями,
группируя набор операций в одну рабочую единицу.
"""

from abc import abstractmethod
from contextlib import AbstractContextManager

from core.domain.base_repositories import IBaseRepository


class IUnitOfWork(AbstractContextManager):
    """Реализация Unit of Work определяет репозитории для различных доменных сущностей."""

    @abstractmethod
    def transaction(self):
        """Контекстный менеджер транзакции."""
        pass

    @abstractmethod
    def get_repo(self, model: type) -> IBaseRepository:
        """Получить репозиторий для указанной ORM модели."""
        pass

    @abstractmethod
    def commit(self):
        """Сохраняет изменения."""
        pass

    @abstractmethod
    def rollback(self):
        """Откатывает изменения."""
        pass
