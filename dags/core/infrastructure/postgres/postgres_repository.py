"""Репозиторий для работы с SQLAlchemy ORM."""

from typing import Any

from core.domain.base_repositories import IBaseRepository
from sqlalchemy import insert
from sqlalchemy.orm import Session


class SqlAlchemyRepository(IBaseRepository):
    """Репозиторий для работы с SQLAlchemy ORM.

    Этот класс является базовой реализацией репозитория для работы
    с таблицами SQLAlchemy. Он предоставляет общие методы для
    взаимодействия с базой данных, такие как добавление, получение,
    обновление и удаление записей.
    """

    orm_model = None

    def __init__(self, session: Session):
        """Инициализация репозитория.

        Args:
            session: SQLAlchemy сессия для взаимодействия с БД.
        """
        self.session = session

    def bulk_insert(self, data: list[dict[str, Any]]) -> int:
        """Выполнить массовое добавление записей в БД.

        Args:
            data: Список словарей, где каждый словарь представляет собой строку для вставки.

        Returns:
            int: Количество вставленных записей
        """
        if not data:
            return 0

        table = self.orm_model.__table__
        result = self.session.execute(insert(table).values(data))

        return result.rowcount or 0
