"""Модуль для работы с MinIO Storage.

Предоставляет класс MinIOClient для взаимодействия с MinIO,
как через Airflow S3Hook, так и напрямую с использованием boto3.
"""

import logging
from typing import List, Optional, Tuple

import boto3
from airflow.exceptions import AirflowException
from botocore.client import Config
from botocore.exceptions import ClientError

try:
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook
except ImportError:
    S3Hook = None

logger = logging.getLogger(__name__)


class MinIOClient:
    """Клиент для работы с MinIO Storage.

    Позволяет взаимодействовать с MinIO как через Airflow S3Hook,
    так и напрямую с использованием boto3.

    Args:
        conn_id (Optional[str]): Идентификатор соединения Airflow S3.
        aws_access_key_id (Optional[str]): Ключ доступа AWS.
        aws_secret_access_key (Optional[str]): Секретный ключ доступа AWS.
        endpoint_url (Optional[str]): URL конечной точки MinIO.
        region_name (str): Название региона AWS. По умолчанию "us-east-1".
        use_airflow (bool): Флаг, указывающий, использовать ли Airflow S3Hook.
                            По умолчанию True. Если True, но S3Hook не
                            импортируется или conn_id не указан, то будет
                            использоваться boto3 напрямую.
    """

    def __init__(
        self,
        conn_id: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region_name: str = "us-east-1",
        use_airflow: bool = True,
    ):
        """Инициализирует клиент MinIO.

        Args:
            conn_id (Optional[str]): Идентификатор соединения Airflow S3.
                                     Используется, если use_airflow=True.
            aws_access_key_id (Optional[str]): Ключ доступа AWS.
                                               Используется, если use_airflow=False.
            aws_secret_access_key (Optional[str]): Секретный ключ доступа AWS.
                                                   Используется, если use_airflow=False.
            endpoint_url (Optional[str]): URL конечной точки MinIO.
                                          Используется, если use_airflow=False.
            region_name (str): Название региона AWS. По умолчанию "us-east-1".
                               Используется, если use_airflow=False.
            use_airflow (bool): Флаг, указывающий, использовать ли Airflow S3Hook.
                                По умолчанию True. Если True, но S3Hook не
                                импортируется или conn_id не указан, то будет
                                использоваться boto3 напрямую.
        """
        self.use_airflow = use_airflow and S3Hook is not None and conn_id is not None
        self.conn_id = conn_id

        if self.use_airflow:
            # Используем Airflow S3Hook
            self.hook = S3Hook(aws_conn_id=conn_id)
        else:
            # Используем boto3 напрямую
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                endpoint_url=endpoint_url,
                region_name=region_name,
                config=Config(s3={"addressing_style": "path"}),
            )

    def check_bucket_exists(self, bucket: str):
        """Проверяет, существует ли бакет.

        Args:
            bucket (str): Название бакета.

        Returns:
            bool: True, если бакет существует, False в противном случае.
        """
        if self.use_airflow:
            return self.hook.check_for_bucket(bucket)
        else:
            try:
                self.s3.head_bucket(Bucket=bucket)
                return True
            except ClientError:
                return False

    def list_files(
        self, bucket: str, prefix: str = "", extensions: Optional[List[str]] = None
    ) -> List[Tuple[str, str]]:
        """Получает список файлов в бакете.

        Args:
            bucket (str): Название бакета.
            prefix (str): Префикс для фильтрации файлов. По умолчанию пустая строка.
            extensions (Optional[List[str]]): Список расширений файлов для фильтрации.
                                              Если None, возвращает все файлы.

        Returns:
            List[Tuple[str, str]]: Список кортежей, где каждый кортеж
                                   состоит из названия бакета и пути к файлу.

        Raises:
            AirflowException: Если произошла ошибка при получении списка файлов.
        """
        try:
            objects = []
            if self.use_airflow:
                objects = self.hook.list_keys(bucket_name=bucket, prefix=prefix)
            else:
                s3_result = self.s3.list_objects_v2(Bucket=bucket)
                for obj in s3_result.get("Contents", []):
                    objects.append(obj["Key"])

            exclude_files = {"success", "error"}

            files = []
            for objname in objects:
                if any(exc in objname for exc in exclude_files):
                    continue

                if extensions:
                    if any(objname.lower().endswith(ext) for ext in extensions):
                        files.append((bucket, objname))
                else:
                    files.append((bucket, objname))

            logger.info(f"Найдено {len(files)} файлов в bucket {bucket}")
            return files

        except Exception as e:
            logger.error(f"Ошибка получения списка файлов: {e}")
            raise AirflowException

    def get_file(self, bucket: str, file_path: str) -> bytes:
        """Загружает файл из бакета.

        Args:
            bucket (str): Название бакета.
            file_path (str): Путь к файлу в бакете.

        Returns:
            bytes: Содержимое файла в виде байтов.

        Raises:
            AirflowException: Если произошла ошибка при загрузке файла.
        """
        try:
            if self.use_airflow:
                response = self.hook.get_key(bucket_name=bucket, key=file_path)
                file_bytes = response.get()["Body"].read()
            else:
                response = self.s3.get_object(Bucket=bucket, Key=file_path)
                file_bytes = response["Body"].read()

            logger.info(f"Загружен файл {file_path} из {bucket}")
            return file_bytes

        except Exception as e:
            logger.error(f"Ошибка загрузки файла {file_path}: {e}")
            raise AirflowException

    def move_file(
        self,
        source_bucket: str,
        source_path: str,
        dest_bucket: str,
        dest_path: str,
    ):
        """Перемещает файл из одного бакета в другой.

        Args:
            source_bucket (str): Название исходного бакета.
            source_path (str): Путь к файлу в исходном бакете.
            dest_bucket (str): Название целевого бакета.
            dest_path (str): Путь к файлу в целевом бакете.

        Raises:
            AirflowException: Если произошла ошибка при перемещении файла.
        """
        try:
            data = self.get_file(source_bucket, source_path)

            if self.use_airflow:
                self.hook.load_bytes(
                    bucket_name=dest_bucket,
                    key=dest_path,
                    bytes_data=data,
                    replace=True,
                )

                # Удаляем оригинал
                self.hook.delete_objects(source_bucket, source_path)
            else:
                copy_source = {
                    "Bucket": source_bucket,
                    "Key": source_path,
                }
                self.s3.copy_object(
                    CopySource=copy_source,
                    Bucket=dest_bucket,
                    Key=dest_path,
                )
                self.s3.delete_object(Bucket=source_bucket, Key=copy_source.get("Key"))

            logger.info(
                f"Файл {source_path} перемещен из {source_bucket} "
                f"в {dest_bucket}/{dest_path}"
            )

        except Exception as e:
            logger.error(f"Ошибка перемещения файла: {e}")
            raise AirflowException
