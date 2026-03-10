"""Базовый класс для обработки Excel файлов.

Этот класс предоставляет общий интерфейс и реализацию для загрузки,
обработки и сохранения данных из Excel файлов. Он предназначен для
использования с SQLAlchemy Unit of Work паттерном и MinIO для хранения файлов.
"""

import logging
from typing import Any, Dict, List

from core.domain.excel import IExcelProcessorBase
from core.infrastructure.unit_of_work.sql_uow import SqlAlchemyUnitOfWork
from utils.minio_client import MinIOClient

logger = logging.getLogger(__name__)


class ExcelProcessorBase(IExcelProcessorBase):
    """Базовый класс для обработки Excel файлов.

    Этот класс предоставляет общий интерфейс и реализацию для загрузки,
    обработки и сохранения данных из Excel файлов. Он предназначен для
    использования с SQLAlchemy Unit of Work паттерном и MinIO для хранения файлов.
    """

    schedule: str = "@daily"

    def __init__(self, uow: SqlAlchemyUnitOfWork):
        """Инициализирует экземпляр ExcelProcessorBase.

        Args:
            uow: Экземпляр SqlAlchemyUnitOfWork для управления транзакциями и репозиторием.
        """
        super().__init__(uow)
        self.uow = uow

    def process(self, file_name: str, data: bytes) -> List[Dict[str, Any]]:
        """Обрабатывает данные из Excel файла.

        Этот метод должен быть реализован в подклассах для определения
        конкретной логики обработки данных из Excel файла.

        Args:
            file_name: Имя файла.
            data: Бинарные данные файла.

        Returns:
            Список словарей, представляющих обработанные данные.

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

    def run(self, file: tuple[str, bytes]) -> List[Dict[str, Any]]:
        """Запускает процесс обработки Excel файла.

        Этот метод принимает кортеж, содержащий имя файла и его бинарные данные,
        и передает их в метод `process` для дальнейшей обработки.

        Args:
            file: Кортеж, содержащий имя файла (str) и бинарные данные файла (bytes).

        Returns:
            Список словарей, представляющих обработанные данные.
        """
        filename, data = file
        return self.process(file_name=filename, data=data)

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
