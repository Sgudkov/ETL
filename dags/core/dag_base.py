"""Базовый класс для Airflow DAGs, управляющих обработкой Excel файлов.

Этот класс предоставляет статические методы для:
- Инициализации и проверки соединений с PostgreSQL и MinIO.
- Получения списка файлов из MinIO.
- Обработки отдельного файла, включая ETL-процесс.
- Перемещения обработанных файлов в соответствующие директории.
"""

import logging
from typing import Type, TypeVar

from airflow.exceptions import AirflowException
from core.excel_processor_base import ExcelProcessorBase
from core.infrastructure.unit_of_work.sql_uow import SqlAlchemyUnitOfWork
from sqlalchemy.orm import sessionmaker
from utils.minio_client import MinIOClient
from utils.postgres_client import PostgresClient

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=ExcelProcessorBase)


class DagBase:
    """Базовый класс для Airflow DAGs, управляющих обработкой Excel файлов.

    Этот класс предоставляет статические методы для:
    - Инициализации и проверки соединений с PostgreSQL и MinIO.
    - Получения списка файлов из MinIO.
    - Обработки отдельного файла, включая ETL-процесс.
    - Перемещения обработанных файлов в соответствующие директории.
    """

    @staticmethod
    def init_validate(
        bucket: str,
        processor_cls: Type[T],
        pg_conn_id: str = "",
        s3_conn_id: str = "",
        **kwargs,
    ) -> bool:
        """Инициализация и проверка соединений с PostgreSQL и MinIO.

        Args:
            bucket (str): Имя бакета MinIO.
            processor_cls (Type[T]): Класс, унаследованный от ExcelProcessorBase,
                                     определяющий логику обработки и модель ORM.
            pg_conn_id (str): Airflow Connection ID для PostgreSQL.
            s3_conn_id (str): Airflow Connection ID для MinIO (S3-совместимого хранилища).
            **kwargs: Дополнительные именованные аргументы:
                use_airflow (bool): Использовать ли Airflow Connections для получения
                                    учетных данных (по умолчанию True).
                aws_access_key_id (str, optional): AWS Access Key ID.
                aws_secret_access_key (str, optional): AWS Secret Access Key.
                endpoint_url (str, optional): URL MinIO сервера.
                pg_uri (str, optional): URI подключения к PostgreSQL.

        Returns:
            bool: True, если инициализация и проверка прошли успешно.

        Raises:
            AirflowException: Если при инициализации или проверке возникла ошибка.
        """
        try:
            use_airflow = kwargs.get("use_airflow", True)
            aws_access_key_id = kwargs.get("aws_access_key_id", None)
            aws_secret_access_key = kwargs.get("aws_secret_access_key", None)
            endpoint_url = kwargs.get("endpoint_url", None)

            minio = MinIOClient(
                conn_id=s3_conn_id,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                endpoint_url=endpoint_url,
                use_airflow=use_airflow,
            )
            minio.check_bucket_exists(bucket)

            pg_uri = kwargs.get("pg_uri", None)

            pg_client = PostgresClient(conn_id=pg_conn_id, uri=pg_uri)

            engine = pg_client.engine
            # Создание таблицы, если отсутствует
            target_schema = processor_cls.orm_model.__table__.schema
            PostgresClient.prepare_database(
                engine, processor_cls.orm_model, target_schema
            )
        except Exception as e:
            logger.error(f"Ошибка при проверке соединений и инициализации данных {e}")
            raise AirflowException

        return True

    @staticmethod
    def get_file_list(bucket: str, s3_conn_id: str = "", **kwargs) -> list:
        """Получение списка файлов из MinIO.

        Args:
            bucket (str): Имя бакета MinIO.
            s3_conn_id (str): Airflow Connection ID для MinIO (S3-совместимого хранилища).
            **kwargs: Дополнительные именованные аргументы:
                use_airflow (bool): Использовать ли Airflow Connections для получения
                                    учетных данных (по умолчанию True).
                aws_access_key_id (str, optional): AWS Access Key ID.
                aws_secret_access_key (str, optional): AWS Secret Access Key.
                endpoint_url (str, optional): URL MinIO сервера.

        Returns:
            list: Список словарей, содержащих метаданные файлов.

        Raises:
            AirflowException: Если при получении списка файлов возникла ошибка.
        """
        use_airflow = kwargs.get("use_airflow", True)
        aws_access_key_id = kwargs.get("aws_access_key_id", None)
        aws_secret_access_key = kwargs.get("aws_secret_access_key", None)
        endpoint_url = kwargs.get("endpoint_url", None)

        minio = MinIOClient(
            conn_id=s3_conn_id,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
            use_airflow=use_airflow,
        )

        try:
            return ExcelProcessorBase.load(bucket=bucket, minio=minio)

        except Exception as e:
            logger.error(f"Ошибка получения фалов {e}")
            raise AirflowException

    @staticmethod
    def process_file(
        file_metadata: dict,
        bucket: str,
        processor_cls: Type[T],
        pg_conn_id: str = "",
        s3_conn_id: str = "",
        **kwargs,
    ) -> dict:
        """Обработка отдельного файла, включая ETL-процесс.

        Args:
            file_metadata (dict): Метаданные файла, включая 'file_name' и 'bucket'.
            bucket (str): Имя бакета MinIO.
            processor_cls (Type[T]): Класс, унаследованный от ExcelProcessorBase,
                                     определяющий логику обработки и модель ORM.
            pg_conn_id (str): Airflow Connection ID для PostgreSQL.
            s3_conn_id (str): Airflow Connection ID для MinIO (S3-совместимого хранилища).
            **kwargs: Дополнительные именованные аргументы:
                use_airflow (bool): Использовать ли Airflow Connections для получения
                                    учетных данных (по умолчанию True).
                aws_access_key_id (str, optional): AWS Access Key ID.
                aws_secret_access_key (str, optional): AWS Secret Access Key.
                endpoint_url (str, optional): URL MinIO сервера.
                pg_uri (str, optional): URI подключения к PostgreSQL.

        Returns:
            dict: Информация об обработанном файле, включая 'file_name', 'bucket' и 'status'.

        Raises:
            AirflowException: Если при обработке файла возникла ошибка.
        """
        pg_uri = kwargs.get("pg_uri", None)

        pg_client = PostgresClient(conn_id=pg_conn_id, uri=pg_uri)
        engine = pg_client.engine
        session_factory = sessionmaker(bind=engine)

        file_metadata["status"] = "success"

        file_name = file_metadata.get("file_name")

        with session_factory() as session:
            uow = SqlAlchemyUnitOfWork(session, processor_cls.repository_class)
            processor = processor_cls(uow)  # Использование переданного класса

            # Скачиваем файл
            use_airflow = kwargs.get("use_airflow", True)
            aws_access_key_id = kwargs.get("aws_access_key_id", None)
            aws_secret_access_key = kwargs.get("aws_secret_access_key", None)
            endpoint_url = kwargs.get("endpoint_url", None)

            minio = MinIOClient(
                conn_id=s3_conn_id,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                endpoint_url=endpoint_url,
                use_airflow=use_airflow,
            )
            file_data = minio.get_file(bucket, file_name)

            # Логика ETL
            processed_data = processor.run((file_name, file_data))
            processor.save(processed_data)

            file_metadata = {
                "file_name": file_name,
                "bucket": bucket,
                "status": "success",
            }

            return file_metadata

    @staticmethod
    def move_file_to(
        processed_data: dict,
        success_path: str,
        error_path: str,
        s3_conn_id: str = "",
        **kwargs,
    ):
        """Перемещение обработанного файла в соответствующую директорию.

        Args:
            processed_data (dict): Информация об обработанном файле, включая 'file_name',
                                   'bucket' и 'status' ('success' или 'error').
            success_path (str): Путь в MinIO для успешно обработанных файлов.
            error_path (str): Путь в MinIO для файлов с ошибками обработки.
            s3_conn_id (str): Airflow Connection ID для MinIO (S3-совместимого хранилища).
            **kwargs: Дополнительные именованные аргументы:
                use_airflow (bool): Использовать ли Airflow Connections для получения
                                    учетных данных (по умолчанию True).
                aws_access_key_id (str, optional): AWS Access Key ID.
                aws_secret_access_key (str, optional): AWS Secret Access Key.
                endpoint_url (str, optional): URL MinIO сервера.

        Raises:
            AirflowException: Если при перемещении файла возникла ошибка.
        """
        use_airflow = kwargs.get("use_airflow", True)
        aws_access_key_id = kwargs.get("aws_access_key_id", None)
        aws_secret_access_key = kwargs.get("aws_secret_access_key", None)
        endpoint_url = kwargs.get("endpoint_url", None)

        minio = MinIOClient(
            conn_id=s3_conn_id,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
            use_airflow=use_airflow,
        )

        source_bucket = processed_data.get("bucket")
        source_path = processed_data.get("file_name")
        dest_bucket = source_bucket

        if processed_data.get("status") == "success":
            dest_path = f"{success_path}/{source_path}"
        else:
            dest_path = f"{error_path}/{source_path}"

        logger.info(f"Перемещаю файл {source_path} из {source_bucket} в {dest_path}")

        minio.move_file(
            source_bucket=source_bucket,
            source_path=source_path,
            dest_bucket=dest_bucket,
            dest_path=dest_path,
        )
