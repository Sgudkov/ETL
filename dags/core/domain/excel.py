"""
Интерфейс для процессоров Excel файлов.

Этот класс определяет базовые методы, которые должен реализовывать любой
процессор Excel файлов. Он включает в себя методы для доступа к репозиторию,
ORM модели, обработки данных, загрузки и сохранения.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Type, TypeVar

from core.domain.unit_of_work import IUnitOfWork
from core.infrastructure.orm.base import Base
from core.infrastructure.repositories.base_sql_repository import SqlAlchemyRepository

# Тип репозитория, который ожидает этот процессор
R = TypeVar("R")


class IExcelProcessorBase(ABC, Generic[R]):
    """Базовый класс для всех процессоров Excel файлов.

    Этот класс служит в качестве абстрактного базового класса (ABC),
    определяя общую структуру и методы, которые должны быть реализованы
    любым процессором Excel файлов. Он обеспечивает стандартизированный
    подход к обработке данных из Excel, включая взаимодействие с
    репозиторием, ORM моделями, загрузкой, сохранением и выполнением
    основного цикла обработки.

    Атрибуты:
        repository_class (Type[SqlAlchemyRepository]): Класс репозитория,
            который будет использоваться для работы с базой данных.
        orm_model (Type[Base]): ORM модель, соответствующая обрабатываемым
            данным.
        dag_id (str): Идентификатор DAG (Directed Acyclic Graph) в оркестраторе
            рабочих процессов (например, Airflow).
        bucket_name (str): Название бакета (bucket) в облачном хранилище
            (например, MinIO), где хранятся файлы.
        schedule (str, optional): Расписание выполнения задачи. По умолчанию "@daily".

    Инициализация:
        __init__(self, uow: IUnitOfWork):
            Инициализирует процессор с объектом Unit of Work для управления
            транзакциями базы данных.

            Args:
                uow (IUnitOfWork): Экземпляр Unit of Work.
    """

    repository_class: Type[SqlAlchemyRepository]
    orm_model: Type[Base]
    dag_id: str
    bucket_name: str
    schedule: str = "@daily"

    def __init__(self, uow: IUnitOfWork):
        """Инициализирует процессор с объектом Unit of Work.

        Args:
            uow (IUnitOfWork): Экземпляр Unit of Work для управления
                транзакциями базы данных.
        """
        self.uow = uow

    @property
    @abstractmethod
    def schema(self) -> str:
        """Абстрактное свойство для схемы."""
        pass

    @abstractmethod
    def process(self, file_name: str, data: bytes) -> List[Dict[str, Any]]:
        """Этот метод отвечает за обработку данных из Excel файла.

        Он принимает имя файла и его содержимое в виде байтов,
        преобразует данные в нужный формат (список словарей) и
        возвращает их.

        Args:
            file_name (str): Имя обрабатываемого Excel файла.
            data (bytes): Содержимое Excel файла в виде байтов.

        Returns:
            List[Dict[str, Any]]: Обработанные данные в виде списка словарей,
                                  где каждый словарь представляет строку из Excel.
        """
        pass

    @staticmethod
    def load(bucket: str, client_minio: object) -> list[str]:
        """Загружает список имен файлов из бакета.

        Args:
            bucket (str): Название бакета, из которого нужно загрузить файлы.
            client_minio (object): Клиент для взаимодействия с MinIO.

        Returns:
            list[str]: Список имен файлов, найденных в бакете.
        """
        pass

    @abstractmethod
    def save(self, data: List[Dict[str, Any]] = None):
        """Сохраняет обработанные данные.

        Args:
            data (List[Dict[str, Any]], optional): Список словарей,
                представляющий собой обработанные данные. Если None,
                метод может выполнять какое-то действие по умолчанию.
        """
        pass

    @abstractmethod
    def run(self, file: tuple[str, bytes]) -> List[Dict[str, Any]]:
        """Основной метод для выполнения полного цикла обработки файла.

        Этот метод координирует загрузку, обработку и сохранение данных
        из Excel файла. Он является точкой входа для выполнения задачи
        обработки файла.

        Args:
            file (tuple[str, bytes]): Кортеж, содержащий имя файла (str)
                                     и его содержимое в виде байтов (bytes).

        Returns:
            List[Dict[str, Any]]: Список словарей, представляющих собой
                                  обработанные данные после всех этапов.
        """
        pass
