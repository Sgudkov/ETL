"""Основной модуль для выполнения локального запуска Excel-процессора.

Этот скрипт инициализирует и запускает экземпляр LocalRun,
передавая ему класс ExcelProcessor1 в качестве процессора Excel.
"""

from core.local_base import LocalRun
from processors import ExcelProcessor1

if __name__ == "__main__":
    local_run = LocalRun(
        excel_processor=ExcelProcessor1
    )

    local_run.run()
