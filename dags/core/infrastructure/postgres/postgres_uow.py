"""Реализация Unit of Work для SQLAlchemy, использующая сессию SQLAlchemy.

Этот класс обеспечивает единый интерфейс для управления транзакциями и
доступа к репозиториям, основанным на SQLAlchemy.
"""

from contextlib import contextmanager
from typing import TypeVar

from core.domain.base_repositories import IBaseRepository
from core.domain.base_uow import IUnitOfWork
from core.infrastructure.postgres.postgres_repository import SqlAlchemyRepository
from sqlalchemy.orm import Session

from core.infrastructure.postgres.repository_factory import RepositoryFactory

T = TypeVar("T", bound=SqlAlchemyRepository)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Реализация Unit of Work для SQLAlchemy, использующая сессию SQLAlchemy.

    Этот класс обеспечивает единый интерфейс для управления транзакциями и
    доступа к репозиториям, основанным на SQLAlchemy.
    """

    def __init__(self, session: Session, repo_factory: RepositoryFactory):
        """Инициализирует экземпляр SqlAlchemyUnitOfWork.

        Args:
            session: Экземпляр SQLAlchemy Session для управления транзакциями и репозиториями.
        """
        self.session = session
        self.repo_factory = repo_factory

    def get_repo(self, model: type) -> IBaseRepository:
        return self.repo_factory.create(model, self.session)

    def commit(self):
        """Фиксирует изменения в базе данных."""
        self.session.commit()

    def rollback(self):
        """Откатывает изменения в базе данных."""
        self.session.rollback()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Управляет жизненным циклом сессии SQLAlchemy.

        Этот метод вызывается при выходе из блока 'with' для управления
        фиксацией или откатом транзакции и закрытием сессии.

        Args:
            exc_type: Тип исключения, если оно возникло.
            exc_val: Значение исключения, если оно возникло.
            exc_tb: Трассировка исключения, если оно возникло.
        """
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.session.close()

    @contextmanager
    def transaction(self):
        """Начинает транзакцию и управляет ее жизненным циклом.

        Этот менеджер контекста обеспечивает, что транзакция либо фиксируется
        при успешном выполнении блока 'with', либо откатывается
        в случае возникновения исключения. Сессия также закрывается
        по завершении транзакции.

        Yields:
            SqlAlchemyUnitOfWork: Сам экземпляр Unit of Work для доступа к репозиториям.
        """
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise
        finally:
            self.session.close()
