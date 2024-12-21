from datetime import datetime
import json
import logging
from src.views import reading_excel_file


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    filename="../logs/services.log",
    filemode="w",
)

cashback_categories_logger = logging.getLogger()

data = reading_excel_file("../data/operations.xlsx")


def cashback_categories(data, year, month) -> str:
    """Функция анализирует, сколько на каждой категории можно заработать кешбэка в указанном месяце года"""
    cashback_categories_logger.info('Начало работы функции анализа кешбэка')

    cashback_distribution = {}

    cashback_categories_logger.info('Преобразование даты в объект datetime')
    for transaction in data:
        date_str = transaction['Дата платежа']

        if isinstance(date_str, str):
            try:
                transaction_date = datetime.strptime(date_str, '%d.%m.%Y')
            except ValueError:
                cashback_categories_logger.error("Неверный формат данных")
                continue
        else:
            cashback_categories_logger.info('date_str не является строкой')
            continue

        if transaction_date.year == year and transaction_date.month == month:
            category = transaction['Категория']
            amount = transaction['Сумма платежа']

            if amount < 0 and category != "Переводы":
                amount = abs(amount)

                if category not in cashback_distribution:
                    cashback_distribution[category] = 0
                cashback_distribution[category] += (amount // 100)
    cashback_categories_logger.info('Создан словаря с данными о кешбэке в указанном месяце')
    sorted_cashback = dict(sorted(cashback_distribution.items(), key=lambda item: item[1], reverse=True))
    cashback_categories_logger.info('Конец работы функции')
    return json.dumps(sorted_cashback, ensure_ascii=False)

result = cashback_categories(data, 2021, 12)
print(result)
