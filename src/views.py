import datetime
import json
from json.decoder import JSONDecodeError
import os
import urllib.request
from typing import Any

import pandas as pd
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    filename="../logs/views.log",
    filemode="w",
)

greeting_by_time_of_day_logger = logging.getLogger()
filter_by_date_logger = logging.getLogger()
reading_excel_file_logger = logging.getLogger()
card_expenses_logger = logging.getLogger()
transaction_rating_logger = logging.getLogger()
exchange_rate_logger = logging.getLogger()
get_price_stock_logger = logging.getLogger()
get_user_settings_logger = logging.getLogger()


load_dotenv()
API_KEY_CUR = os.getenv("API_KEY_CUR")
SP_500_API_KEY = os.getenv("SP_500_API_KEY")

date_now = datetime.datetime.now()


def greeting_by_time_of_day(date_now: datetime) -> str:
    """Функция выводит различное приветствие в зависимости от времени суток"""
    greeting_by_time_of_day_logger.info('Начало работы функции вывода приветствия')
    hour = date_now.hour
    if 6 <= hour < 12:
        greeting = "Доброе утро!"
    elif 12 <= hour < 18:
        greeting = "Добрый день!"
    elif 18 <= hour < 23:
        greeting = "Добрый вечер!"
    else:
        greeting = "Доброй ночи!"
    greeting_by_time_of_day_logger.info('Функция возвращает приветствие в зависимости от времени')
    return greeting


def filter_by_date(date: str, my_list: list) -> list:
    """Функция фильтрующая данные по заданной дате"""
    list_by_date = []
    filter_by_date_logger.info('Начало работы функции фильтрующей данные дате')
    if date == "":
        return list_by_date
    year, month, day = int(date[0:4]), int(date[5:7]), int(date[8:10])
    date_obj = datetime.datetime(year, month, day)
    for i in my_list:
        if i["Дата платежа"] == "nan" or type(i["Дата платежа"]) is float:
            continue
        elif (
                date_obj
                >= datetime.datetime.strptime(str(i["Дата платежа"]), "%d.%m.%Y")
                >= date_obj - datetime.timedelta(days=day - 1)
        ):
            list_by_date.append(i)
    filter_by_date_logger.info('Конец работы функции фильтрующей данные по дате')
    return list_by_date


def reading_excel_file(file_excel: str) -> list:
    """Функция считывает excel-файл и возвращает список словарей"""
    reading_excel_file_logger.info('Начало работы функции считывающей excel-файл')
    try:
        reader = pd.read_excel(file_excel)
        result = reader.apply(
            lambda row: {
                "Дата платежа": row["Дата платежа"],
                "Номер карты": row["Номер карты"],
                "Статус": row["Статус"],
                "Сумма платежа": row["Сумма платежа"],
                "Валюта платежа": row["Валюта платежа"],
                "Категория": row["Категория"],
                "MCC": row["MCC"],
                "Описание": row["Описание"],
            },
            axis=1
        ).tolist()
        reading_excel_file_logger.info('Создан список словарей финансовых транзакций')
        return result
    except FileNotFoundError:
        reading_excel_file_logger.error("Файл с транзакциями не найден")
        return []


def card_expenses(my_list: list) -> Any:
    """Функция выводит последние 4 цифры карты, сумму расходов и кешбэк"""

    cards = {}
    information_on_cards = []
    card_expenses_logger.info('Начало работы функции с данными по карте')

    for transaction in my_list:
        if transaction["Номер карты"] == "nan" or type(transaction["Номер карты"]) is float:
            continue
        elif transaction["Сумма платежа"] == "nan":
            continue
        else:
            if transaction["Номер карты"][1:] in cards:
                cards[transaction["Номер карты"][1:]] += float(str(transaction["Сумма платежа"])[1:])
            else:
                cards[transaction["Номер карты"][1:]] = float(str(transaction["Сумма платежа"])[1:])
    card_expenses_logger.info('Формирование списка словарей с данными по картам')
    for k, v in cards.items():
        information_on_cards.append({"last_digits": k, "total_spent": round(v, 2), "cashback": round(v / 100, 2)})
    card_expenses_logger.info('Конец работы функции с данными по карте')
    return information_on_cards


def transaction_rating_by_amount(my_list: list) -> list[dict]:
    """Функция выводит топ-5 транзакций по сумме платежа"""
    all_expenses = []
    top_five_transaction = []
    transaction_rating_logger.info('Начало работы функции выводящей топ-5 транзакций')
    for transaction in my_list:
        if transaction["Категория"] != "Пополнения":
            all_expenses.append(transaction)
        else:
            continue
    sorted_transactions = sorted(all_expenses, key=lambda x: x["Сумма платежа"], reverse=True)[:5]
    transaction_rating_logger.info('Формирование списка словарей топ-5 транзакций')
    for transaction in sorted_transactions:
        top_five_transaction.append(
            {
                "date": transaction["Дата платежа"],
                "amount": transaction["Сумма платежа"],
                "category": transaction["Категория"],
                "description": transaction["Описание"],
            }
        )
    transaction_rating_logger.info('Конец работы функции выводящей топ-5 транзакцийе')
    return top_five_transaction


def exchange_rate(currency: dict) -> list[dict]:
    """Функция выводит актуальную информацию о курсе валют"""
    api_key = API_KEY_CUR
    result = []
    exchange_rate_logger.info('Начало работы функции с информацией о курсе валют')

    for i in currency:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{i}"

        with urllib.request.urlopen(url) as response:
            body_json = response.read()
        body_dict = json.loads(body_json)
        result.append({"currency": i, "rate": round(body_dict["conversion_rates"]["RUB"], 2)})
        exchange_rate_logger.info("Создание списка словарей с данными о курсе валют")

    exchange_rate_logger.info('Конец работы функции с информацией о курсе валют')
    return result


def get_price_stock(stocks: dict) -> list:
    """Функция для получения данных об акциях из списка S&P500"""

    get_price_stock_logger.info('Начало работы функции с информацией об акциях')
    api_key = SP_500_API_KEY
    stock_prices = []

    get_price_stock_logger.info("Функция обрабатывает данные транзакций.")
    for stock in stocks:
        get_price_stock_logger.info("Перебор акций в списке 'stocks'")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        response = requests.get(url, timeout=5, allow_redirects=False)
        result = response.json()

        get_price_stock_logger.info('Формирование списка словарей с данными об акциях')
        stock_prices.append({"stock": stock, "price": round(float(result["Global Quote"]["05. price"]), 2)})
        get_price_stock_logger.info('Конец работы функции с информацией об акциях')
    return stock_prices


def get_user_settings(path: str) -> list:
    """Функция принимает на вход путь до JSON-файла и возвращает список словарей с данными об валютах и акциях"""
    get_user_settings_logger.info("Начало работы функции преобразующей JSON-файл")
    try:
        with open(path, encoding="utf-8") as file:
            try:
                user_settings = json.load(file)
                get_user_settings_logger.info("Создан список словарей с данными об валютах и акциях")
                return user_settings
            except JSONDecodeError:
                get_user_settings_logger.error("Ошибка файла с транзакциями")
                return []
    except FileNotFoundError:
        get_user_settings_logger.error("Файл с транзакциями не найден")
        return []
