"""Обработчик для Excel-файла.

Загружает данные из Excel-файла, преобразует их в DataFrame pandas
и затем возвращает данные в виде списка словарей.
"""

from io import BytesIO
from typing import Any, Dict, List

import pandas as pd

from core.excel_processor_base import ExcelProcessorBase
from orm.table1_orm import ExcelTable1ORM
from repositories.excel1_repositories import Excel1Repository


class ExcelProcessor1(ExcelProcessorBase):
    repository_class = Excel1Repository
    dag_id = 'ExcelProcessor1'
    orm_model = ExcelTable1ORM
    bucket_name = 'excelbucket'

    def process(self, file_name: str, data: bytes) -> List[Dict[str, Any]]:
        df = pd.read_excel(BytesIO(data), engine='openpyxl', header=None)
        df.columns = [x for x in self.orm_model.__table__.columns.keys() if x !='id']
        return df.to_dict(orient='records')

