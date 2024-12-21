import datetime
import json
import pandas as pd
from typing import Optional
from typing import Any
import logging

from src.decorators import decorator_spending_by_category
from src.views import reading_excel_file


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    filename="../logs/reports.log",
    filemode="w",
)

spending_by_category_logger = logging.getLogger()

@decorator_spending_by_category
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> Any:
    """Функция возвращающая траты за последние 3 месяца по заданной категории"""
    spending_by_category_logger.info("Начало работы")

    list_by_category = []
    final_list = []

    for transaction in transactions:
        spending_by_category_logger.info("Обработка условия на отсутствие")
        if date is None:
            date_start = datetime.datetime.now() - datetime.timedelta(days=90)
            if transaction['Категория'] == category:
                list_by_category.append(transaction)
            for transaction in list_by_category:
                if transaction["Дата платежа"] == "nan" or type(transaction["Дата платежа"]) is float:
                    continue
                elif (
                        date_start
                        <= datetime.datetime.strptime(str(transaction["Дата платежа"]), "%d.%m.%Y")
                        <= date_start + datetime.timedelta(days=90)
                ):
                    final_list.append(
                            {
                "date": transaction["Дата платежа"],
                "amount": transaction["Сумма платежа"]
            }
                        )
            return final_list
        else:
            spending_by_category_logger.info("Обработка условия на создание")
            day, month, year = date.split(".")
            date_obj = datetime.datetime(int(year), int(month), int(day))
            date_start = date_obj - datetime.timedelta(days=90)

            for transaction in transactions:
                if transaction["Категория"] == category:
                    list_by_category.append(transaction)

            for transaction in list_by_category:
                if transaction["Дата платежа"] == "nan" or type(transaction["Дата платежа"]) is float:
                    continue
                else:
                    day_, month_, year_ = transaction["Дата платежа"].split(".")
                    date_obj_ = datetime.datetime(int(year), int(month), int(day))
                    if date_start <= date_obj_ <= date_start + datetime.timedelta(days=90):
                        final_list.append(
                            {
                "date": transaction["Дата платежа"],
                "amount": transaction["Сумма платежа"]
            }
                        )
            spending_by_category_logger.info("Завершение работы функции")
            data_json = json.dumps(final_list, indent=4, ensure_ascii=False)

            return data_json

f = reading_excel_file("../data/operations.xlsx")
print(spending_by_category(f, 'Супермаркеты', '01.10.2021'))