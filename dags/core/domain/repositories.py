"""Абстрактный базовый класс для репозиториев.

Этот класс определяет интерфейс для работы с хранилищем данных,
позволяя абстрагироваться от конкретной реализации (например, SQLAlchemy, Django ORM, Plain Python lists).

Generic[T]: Generic параметр, представляющий тип ORM-модели или данных, с которыми работает репозиторий.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class IBaseRepository(ABC, Generic[T]):
    """Абстрактный базовый класс для репозиториев.

    Этот класс определяет интерфейс для работы с хранилищем данных,
    позволяя абстрагироваться от конкретной реализации (например, SQLAlchemy, Django ORM, Plain Python lists).

    Generic[T]: Generic параметр, представляющий тип ORM-модели или данных, с которыми работает репозиторий.
    """

    orm_model: Optional[type[T]]

    @abstractmethod
    def bulk_insert(self, data: list[dict[str, Any]]) -> int:
        """Вставляет пачку данных в хранилище.

        Args: data: Список словарей, каждый из которых представляет собой запись для вставки.
        Returns: Количество успешно вставленных записей.
        """
        pass
