"""Модуль для работы с PostgreSQL.

Представляет класс PostgresClient, используемый для взаимодействия с базами данных PostgreSQL,
опционально с использованием Airflow для управления подключениями.
"""

import logging
from typing import Optional

from sqlalchemy import create_engine, schema
from sqlalchemy.engine import Engine

from core.infrastructure.repositories.base_sql_repository import SqlAlchemyRepository

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
except ImportError:
    PostgresHook = None

logger = logging.getLogger(__name__)


class PostgresClient:
    """Клиент для работы с PostgreSQL.

    Args:
        conn_id (Optional[str]): Идентификатор соединения Airflow.
        uri (Optional[str]): Строка подключения SQLAlchemy.
        use_airflow (bool): Использовать ли Airflow для управления подключениями.
    """

    def __init__(
            self,
            conn_id: Optional[str] = None,
            uri: Optional[str] = None,
            use_airflow: bool = True,
    ):
        """Инициализация клиента PostgreSQL.

        Args:
            conn_id (Optional[str]): Идентификатор соединения Airflow.
            uri (Optional[str]): Строка подключения SQLAlchemy.
            use_airflow (bool): Использовать ли Airflow для управления подключениями.
        """
        self.use_airflow = use_airflow and PostgresHook is not None and conn_id

        if self.use_airflow:
            if not conn_id:
                raise ValueError("conn_id должен быть указан")

            hook = PostgresHook(postgres_conn_id=conn_id)
            self._engine: Engine = hook.get_sqlalchemy_engine()
        else:
            if not uri:
                raise ValueError("URI должен быть указан, если Airflow не используется")

            self._engine: Engine = create_engine(uri)

    @property
    def engine(self) -> Engine:
        """Получает объект соединения с базой данных."""
        return self._engine

    @staticmethod
    def prepare_database(engine: Engine, orm_models: list[SqlAlchemyRepository]):
        """Подготавливает базу данных.

        Создает схему, если она не существует, и создает таблицы,
        определенные ORM-моделью.

        Args:
            engine (Engine): Объект соединения с базой данных SQLAlchemy.
            orm_models (objects): ORM-модели, содержащая определение таблиц.
        """

        with engine.begin() as conn:

            for models in orm_models:
                table = models.orm_model.__table__
                if table.schema and table.schema != "public":
                    if not conn.dialect.has_schema(conn, table.schema):
                        conn.execute(schema.CreateSchema(table.schema))

                table.create(bind=conn, checkfirst=True)
