from typing import Any, Dict, List

from core.excel_processor_base import ExcelProcessorBase
from orm.table2_orm import ExcelTable2ORM
from repositories.excel2_repositories import Excel2Repository


class ExcelProcessor2(ExcelProcessorBase):
    repository_class = Excel2Repository
    dag_id = 'ExcelProcessor2'
    orm_model = ExcelTable2ORM

    def process(self, file_name: str, data: bytes) -> List[Dict[str, Any]]:
        pass