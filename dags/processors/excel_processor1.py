"""Обработчик для Excel-файла.

Загружает данные из Excel-файла, преобразует их в DataFrame pandas
и затем возвращает данные в виде списка словарей.
"""

from io import BytesIO

import pandas as pd

from core.excel_processor_base import ExcelProcessorBase
from orm.table1_orm import ExcelTable1ORM
from orm.table2_orm import ExcelTable2ORM
from repositories.excel1_repositories import Excel1Repository
from repositories.excel2_repositories import Excel2Repository


class ExcelProcessor1(ExcelProcessorBase):
    repository_classes = {
        ExcelTable1ORM: Excel1Repository,
        ExcelTable2ORM: Excel2Repository,
    }
    dag_id = "ExcelProcessor1"
    bucket_name = "excelbucket"

    def process(self, file_name: str, data: bytes) -> dict[type, list[dict]]:
        df = pd.read_excel(BytesIO(data), engine="openpyxl", header=None)
        df.columns = [x for x in ExcelTable1ORM.__table__.columns.keys() if x != "id"]
        return {ExcelTable1ORM: df.to_dict(orient="records")}
