"""Обработчик для Excel-файла.

Загружает данные из Excel-файла, преобразует их в DataFrame pandas
и затем возвращает данные в виде списка словарей.
"""

from io import BytesIO

import pandas as pd

from core.application.excel_processor_base import ExcelProcessorBase
from processors.processor_1.orm.table1_orm import ExcelTable1ORM
from processors.processor_1.repositories.excel1_repositories import Excel1Repository


class ExcelProcessor1(ExcelProcessorBase):
    repository_classes = {
        ExcelTable1ORM: Excel1Repository,
    }
    dag_id = "ExcelProcessor1"
    bucket_name = "excelbucket"

    def process(self, file_name: str, data: bytes) -> dict[type, list[dict]]:
        df = pd.read_excel(BytesIO(data), engine="openpyxl", header=None)
        df.columns = [x for x in ExcelTable1ORM.__table__.columns.keys() if x != "id"]
        return {ExcelTable1ORM: df.to_dict(orient="records")}
