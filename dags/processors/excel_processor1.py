"""Обработчик для Excel-файла.

Загружает данные из Excel-файла, преобразует их в DataFrame pandas
и затем возвращает данные в виде списка словарей.
"""

from io import BytesIO

import pandas as pd

from core.excel_processor_base import ExcelProcessorBase
from repositories.excel1_repositories import Excel1Repository
from repositories.excel2_repositories import Excel2Repository


class ExcelProcessor1(ExcelProcessorBase):
    repository_classes = {"stg": Excel1Repository, "raw": Excel2Repository}
    dag_id = "ExcelProcessor1"
    bucket_name = "excelbucket"

    def process(self, file_name: str, data: bytes) -> dict[str, list[dict]]:
        df = pd.read_excel(BytesIO(data), engine="openpyxl", header=None)
        df.columns = [
            x
            for x in self.repository_classes.get(
                "stg"
            ).orm_model.__table__.columns.keys()
            if x != "id"
        ]
        return {"stg": df.to_dict(orient="records")}
