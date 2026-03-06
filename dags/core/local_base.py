"""Класс для локального запуска ETL-процессов.

Этот класс предназначен для выполнения ETL-задач на локальной машине,
без использования оркестратора Airflow. Он инициализирует необходимые
компоненты, получает список файлов из S3-бакета, обрабатывает каждый файл
с использованием указанного Excel-процессора и перемещает файл в
соответствующую директорию (success или error) в зависимости от результата
обработки.
"""

import logging
from typing import Type, TypeVar

from config.settings import settings
from core.dag_base import DagBase
from core.excel_processor_base import ExcelProcessorBase
from core.infrastructure.repositories.base_sql_repository import \
    SqlAlchemyRepository
from core.infrastructure.unit_of_work.sql_uow import SqlAlchemyUnitOfWork
from processors import ExcelProcessor1

T = TypeVar("T", bound=ExcelProcessorBase)
S = TypeVar("S", bound=SqlAlchemyUnitOfWork)
V = TypeVar("V", bound=SqlAlchemyRepository)

logger = logging.getLogger(__name__)


class LocalRun:
    """Класс для локального запуска ETL-процессов.

    Этот класс предназначен для выполнения ETL-задач на локальной машине,
    без использования оркестратора Airflow. Он инициализирует необходимые
    компоненты, получает список файлов из S3-бакета, обрабатывает каждый файл
    с использованием указанного Excel-процессора и перемещает файл в
    соответствующую директорию (success или error) в зависимости от результата
    обработки.
    """

    def __init__(self, excel_processor: Type[T]):
        """Инициализирует экземпляр LocalRun.

        Args:
            excel_processor: Класс процессора Excel, который будет использоваться
                             для обработки файлов.
        """
        self.processor = excel_processor

    def run(self):
        """Запускает ETL-процессы локально.

        Этот метод выполняет следующие действия:
        1. Проводит валидацию конфигурации и необходимых параметров с помощью
           `DagBase.init_validate`.
        2. Получает список файлов из указанного S3-бакета с помощью
           `DagBase.get_file_list`.
        3. Итерируется по каждому файлу в списке:
           a. Пытается обработать файл с использованием указанного класса
              Excel-процессора (`self.processor`) через `DagBase.process_file`.
           b. Если обработка прошла успешно, добавляет статус "success" к
              информации о файле.
           c. Если в процессе обработки возникла ошибка, логирует ошибку и
              добавляет статус "error" к информации о файле.
           d. Перемещает обработанный файл в директорию "success" или "error"
              в S3 бакете в зависимости от его статуса, используя
              `DagBase.move_file_to`.
        """
        processor_cls = self.processor

        DagBase.init_validate(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            use_airflow=False,
            pg_uri=settings.LOCAL_PG_URL,
            bucket=ExcelProcessor1.bucket_name,
            processor_cls=processor_cls,
        )

        file_list = DagBase.get_file_list(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            use_airflow=False,
            bucket=ExcelProcessor1.bucket_name,
        )

        for file in file_list:
            try:
                DagBase.process_file(
                    file,
                    bucket=ExcelProcessor1.bucket_name,
                    processor_cls=processor_cls,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                    use_airflow=False,
                    pg_uri=settings.LOCAL_PG_URL,
                )
                file["status"] = "success"
            except Exception as e:
                logger.error(f"Error processing file {file['name']}: {e}")
                file["status"] = "error"

            DagBase.move_file_to(
                processed_data=file,
                success_path="success",
                error_path="error",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                use_airflow=False,
            )
