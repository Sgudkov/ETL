"""Модуль репозиториев для работы с excel данными в базе данных."""

from core.infrastructure.repositories.base_sql_repository import \
    SqlAlchemyRepository
from orm.table2_orm import ExcelTable2ORM


class Excel2Repository(SqlAlchemyRepository):
    """Репозиторий для работы с excel данными в базе данных."""

    orm_model = ExcelTable2ORM
