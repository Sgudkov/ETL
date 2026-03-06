"""Модуль репозиториев для работы с excel данными в базе данных."""

from core.infrastructure.repositories.base_sql_repository import \
    SqlAlchemyRepository
from orm.table1_orm import ExcelTable1ORM


class Excel1Repository(SqlAlchemyRepository):
    """Репозиторий для работы с excel данными в базе данных."""

    orm_model = ExcelTable1ORM
