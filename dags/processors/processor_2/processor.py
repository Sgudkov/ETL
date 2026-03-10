from core.application.excel_processor_base import ExcelProcessorBase
from processors.processor_2.orm.table2_orm import ExcelTable2ORM
from processors.processor_2.repositories.excel2_repositories import Excel2Repository


class ExcelProcessor2(ExcelProcessorBase):
    repository_class = {
        ExcelTable2ORM: Excel2Repository
    }
    dag_id = 'ExcelProcessor2'
    orm_model = ExcelTable2ORM

    def process(self, file_name: str, data: bytes) -> dict[type,list[dict]]:
        pass