from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ExcelTable1ORM(Base):
    __tablename__ = 'table1'

    __table_args__ = {
        "schema": "finance_dept",
        "comment": "Таблица для отчетов финансового отдела"
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    field1 = Column(String)
    field2 = Column(Integer)
    field3 = Column(String)
    field4 = Column(Integer)
    field5 = Column(String)
