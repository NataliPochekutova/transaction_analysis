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

    final_list = []

    if date is None:
        date_start = datetime.datetime.now() - datetime.timedelta(days=90)
    else:
        day, month, year = date.split(".")
        date_obj = datetime.datetime(int(year), int(month), int(day))
        date_start = date_obj - datetime.timedelta(days=90)

    for index, transaction in transactions.iterrows():
        if transaction['Категория'] == category:

            if pd.isna(transaction["Дата платежа"]) or isinstance(transaction["Дата платежа"], float):
                continue
            try:
                transaction_date = datetime.datetime.strptime(str(transaction["Дата платежа"]), "%d.%m.%Y")
                if date_start <= transaction_date <= date_start + datetime.timedelta(days=90):
                    final_list.append({
                        "date": transaction["Дата платежа"],
                        "amount": transaction["Сумма платежа"]
                    })
            except ValueError:
                continue

    return json.dumps(final_list, indent=4, ensure_ascii=False)


f = pd.DataFrame(reading_excel_file("../data/operations.xlsx"))
print(spending_by_category(f, 'Супермаркеты', '01.10.2021'))
