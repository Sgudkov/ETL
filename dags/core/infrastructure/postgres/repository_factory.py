"""
Фабрика для создания репозиториев.

Этот класс отвечает за создание экземпляров репозиториев на основе
типов моделей к классам репозиториев.
"""

from sqlalchemy.orm import Session

from core.domain.base_repositories import IBaseRepository


class RepositoryFactory:
    """Фабрика для создания репозиториев.

    Этот класс отвечает за создание экземпляров репозиториев на основе
    типов моделей к классам репозиториев.
    """

    def __init__(self, mapping: dict[type, type[IBaseRepository]]):
        """Инициализирует фабрику репозиториев.

        Args:
            mapping: Словарь, сопоставляющий типы моделей с классами репозиториев.
        """
        self.mapping = mapping

    def create(self, model: type, session: Session) -> IBaseRepository:
        """Создает экземпляр репозитория для данной модели.

        Args:
            model: Тип модели, для которой нужно создать репозиторий.
            session: SQLAlchemy сессия для репозитория.

        Returns:
            Экземпляр репозитория.
        """
        repo_cls = self.mapping[model]
        return repo_cls(session)
