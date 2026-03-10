from sqlalchemy.orm import Session

from core.domain.repositories import IBaseRepository
from core.infrastructure.repositories.base_sql_repository import SqlAlchemyRepository


class RepositoryFactory:
    def __init__(self, mapping: dict[type, type[IBaseRepository]]):
        self.mapping = mapping

    def create(self, model: type, session: Session):
        repo_cls = self.mapping[model]
        return repo_cls(session)
