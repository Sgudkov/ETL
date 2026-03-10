from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ExcelTable2ORM(Base):
    __tablename__ = 'table2'

    __table_args__ = {
        "schema": "product_dept",
        "comment": "Таблица для отчетов  продуктового отдела"
    }

    id = Column(Integer, primary_key=True)

    field1 = Column(String)
    field2 = Column(Integer)
    field3 = Column(String)
    field4 = Column(Integer)
    field5 = Column(String)
