import json
import logging
from src.views import greeting_by_time_of_day, filter_by_date, reading_excel_file, card_expenses
from src.views import transaction_rating_by_amount, exchange_rate, get_price_stock, date_now, get_user_settings


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    filename="../logs/views.log",
    filemode="w",
)

main_logger = logging.getLogger()

my_list = reading_excel_file("../data/operations.xlsx")
user_settings = get_user_settings("../data/user_settings.json")
stocks = user_settings["user_stocks"]
currency = user_settings["user_currencies"]


def main(user_data: str, stocks: dict, currency: dict) -> str:
    """Функция создающая JSON ответ для страницы главная"""
    main_logger.info('Начало работы функции main')
    final_list = filter_by_date(user_data, my_list)
    greeting = greeting_by_time_of_day(date_now)
    cards = card_expenses(final_list)
    top_trans = transaction_rating_by_amount(final_list)
    stocks_prices = get_price_stock(stocks)
    currency_r = exchange_rate(currency)
    main_logger.info('Формирование JSON ответа')
    result = [{
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_trans,
        "currency_rates": currency_r,
        "stock_prices": stocks_prices,
    }]
    date_json = json.dumps(
        result,
        indent=4,
        ensure_ascii=False,
    )
    main_logger.info("Завершение работы функции main")
    return date_json


print(main('2021-10-20', stocks, currency))
