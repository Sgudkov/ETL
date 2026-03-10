"""Базовый класс для обработки Excel файлов.

Этот класс предоставляет общий интерфейс и реализацию для загрузки,
обработки и сохранения данных из Excel файлов. Он предназначен для
использования с SQLAlchemy Unit of Work паттерном и MinIO для хранения файлов.
"""

import logging

from core.domain.base_processor import IExcelProcessorBase
from core.domain.base_repositories import IBaseRepository
from core.infrastructure.postgres.postgres_uow import SqlAlchemyUnitOfWork
from core.infrastructure.minio.minio_client import MinIOClient

logger = logging.getLogger(__name__)


class ExcelProcessorBase(IExcelProcessorBase):
    """Базовый класс для обработки Excel файлов.

    Этот класс предоставляет общий интерфейс и реализацию для загрузки,
    обработки и сохранения данных из Excel файлов. Он предназначен для
    использования с SQLAlchemy Unit of Work паттерном и MinIO для хранения файлов.
    """

    repository_classes: dict[type, type[IBaseRepository]]
    dag_id: str
    bucket_name: str
    schedule: str = "@daily"

    def __init__(self, uow: SqlAlchemyUnitOfWork):
        """Инициализирует экземпляр ExcelProcessorBase.

        Args:
            uow: Экземпляр SqlAlchemyUnitOfWork для управления транзакциями и репозиторием.
        """
        self.uow = uow

    def process(self, file_name: str, data: bytes) -> dict[type, list[dict]]:
        """Обрабатывает данные из Excel файла.

        Этот метод должен быть реализован в подклассах для определения
        конкретной логики обработки данных из Excel файла.

        Args:
            file_name: Имя файла.
            data: Бинарные данные файла.

        Returns:
            Словарь, представляющих обработанные данные.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError

    def save(self, data: dict[type, list[dict]] = None) -> int:
        """Сохраняет обработанные данные в базу данных.

        Args:
            data: Словари, представляющих обработанные данные для сохранения.
                  Если None, функция вернет 0.

        Returns:
            int: Количество успешно сохраненных записей.
        """
        if not data:
            return 0

        with self.uow.transaction():
            count = 0
            for model, rows in data.items():
                repo = self.uow.get_repo(model)
                count += repo.bulk_insert(rows)

        return count

    def run(self, file: tuple[str, bytes]):
        """Запускает процесс обработки Excel файла.

        Этот метод принимает кортеж, содержащий имя файла и его бинарные данные,
        и передает их в метод `process` для дальнейшей обработки.

        Args:
            file: Кортеж, содержащий имя файла (str) и бинарные данные файла (bytes).

        """
        filename, data = file
        data = self.process(file_name=filename, data=data)
        self.save(data)

    @staticmethod
    def load(bucket: str, minio: MinIOClient) -> list[dict]:
        """Загружает список файлов Excel из указанного бакета MinIO.

        Этот статический метод ищет файлы с расширениями `.xlsx`, `.xls`, `.xlsm`, `.xlsb`
        в заданном бакете MinIO и возвращает список словарей, где каждый словарь
        содержит информацию о бакете и имени файла.

        Args:
            bucket: Название бакета MinIO, из которого нужно загрузить файлы.
            minio: Экземпляр клиента MinIOClient для взаимодействия с MinIO.

        Returns:
            Список словарей, где каждый словарь имеет ключи 'bucket' и 'file_name',
            представляющих найденные файлы Excel.
        """
        list_files = minio.list_files(
            bucket=bucket,
            extensions=[".xlsx", ".xls", ".xlsm", ".xlsb"],
        )

        return [{"bucket": bucket, "file_name": filename} for _, filename in list_files]
