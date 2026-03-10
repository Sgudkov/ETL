"""Модуль репозиториев для работы с excel данными в базе данных."""

from core.infrastructure.postgres.postgres_repository import \
    SqlAlchemyRepository
from processors.processor_1.orm.table1_orm import ExcelTable1ORM


class Excel1Repository(SqlAlchemyRepository):
    """Репозиторий для работы с excel данными в базе данных."""

    orm_model = ExcelTable1ORM
