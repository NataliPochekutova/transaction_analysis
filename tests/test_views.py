import pytest
import pandas as pd
from unittest.mock import patch, Mock, mock_open
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from src.views import greeting_by_time_of_day, filter_by_date, reading_excel_file, card_expenses
from src.views import transaction_rating_by_amount, exchange_rate, get_price_stock, get_user_settings


load_dotenv()
API_KEY_CUR = os.getenv("API_KEY_CUR")


test_cases = [
    (datetime(2023, 10, 20, 7, 0), "Доброе утро!"),
    (datetime(2023, 10, 20, 13, 0), "Добрый день!"),
    (datetime(2023, 10, 20, 19, 0), "Добрый вечер!"),
    (datetime(2023, 10, 20, 23, 30), "Доброй ночи!"),
    (datetime(2023, 10, 20, 2, 0), "Доброй ночи!")
]


@pytest.mark.parametrize("date_now, expected_greeting", test_cases)
def test_greeting_by_time_of_day(date_now, expected_greeting):
    """Тестирование функции вывода приветствия в зависимости от времени суток"""
    assert greeting_by_time_of_day(date_now) == expected_greeting


def test_filter_valid_date(sample_data):
    """Тестирование функции фильтрации данных по заданной дате"""
    result = filter_by_date("2021-11-03", sample_data)
    expected = [
        {'Дата платежа': '01.11.2021', 'Статус': 'OK', 'Сумма платежа': -228.0, 'Валюта платежа': 'RUB',
         'Категория': 'Супермаркеты', 'Описание': 'Колхоз', 'MCC': 5411, 'Номер карты': '*4556'},
        {'Дата платежа': '02.11.2021', 'Статус': 'OK', 'Сумма платежа': -110.0, 'Валюта платежа': 'RUB',
         'Категория': 'Фастфуд', 'Описание': 'Mouse Tail', 'MCC': 5411, 'Номер карты': '*4556'},
        {'Дата платежа': '03.11.2021', 'Статус': 'OK', 'Сумма платежа': -525.0, 'Валюта платежа': 'RUB',
         'Категория': 'Одежда и обувь', 'Описание': 'WILDBERRIES', 'MCC': 5399, 'Номер карты': '*7197'}
    ]
    assert result == expected


def test_filter_empty_date(sample_data):
    """фильтрация данных по дате, где вместо даты пустая строка"""
    result = filter_by_date("", sample_data)
    expected = []
    assert result == expected


def test_filter_no_matching_dates(sample_data):
    """фильтрация данных по дате, где дата не входит в диапазон"""
    result = filter_by_date("2021-12-03", sample_data)
    expected = []
    assert result == expected


def test_filter_with_nan(sample_data):
    """Тестирование функции фильтрации данных по заданной дате"""
    result = filter_by_date("2021-11-01", sample_data)
    expected = [
        {'Дата платежа': '01.11.2021', 'Статус': 'OK', 'Сумма платежа': -228.0, 'Валюта платежа': 'RUB',
         'Категория': 'Супермаркеты', 'Описание': 'Колхоз', 'MCC': 5411, 'Номер карты': '*4556'}
    ]
    assert result == expected


@patch('pandas.read_excel')
def test_reading_excel_file(mock_read_excel, sample_data):
    """Тестирование функции чтения из Excel файла"""
    mock_read_excel.return_value = pd.DataFrame(sample_data)
    result = reading_excel_file("mock_file.xlsx")
    expected = [
        {
            "Дата платежа": "01.11.2021",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма платежа": -228.0,
            "Валюта платежа": "RUB",
            "Категория": "Супермаркеты",
            "MCC": 5411,
            "Описание": "Колхоз"
        },
        {
            'Дата платежа': '02.11.2021',
            'Номер карты': '*4556',
            'Статус': 'OK',
            'Сумма платежа': -110.0,
            'Валюта платежа': 'RUB',
            'Категория': 'Фастфуд',
            'MCC': 5411,
            'Описание': 'Mouse Tail',
         },
        {
            "Дата платежа": "03.11.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма платежа": -525.0,
            "Валюта платежа": "RUB",
            "Категория": "Одежда и обувь",
            "MCC": 5399,
            "Описание": "WILDBERRIES"
        }
    ]
    assert result == expected
    mock_read_excel.assert_called_once_with("mock_file.xlsx")


@patch('pandas.read_excel')
def test_reading_excel_file_file_not_found(mock_read_excel):
    """Тестирование чтения Excel файла, если файл не найден"""
    mock_read_excel.side_effect = FileNotFoundError
    result = reading_excel_file("non_existing_file.xlsx")
    assert result == []


def test_card_expenses(sample_data):
    """Тестирование функции, возвращающей данные по карте"""
    result = card_expenses(sample_data)

    expected = [
        {"last_digits": "4556", "total_spent": 338.0, "cashback": 3.38},
        {"last_digits": "7197", "total_spent": 525.0, "cashback": 5.25}
    ]
    assert result == expected


def test_card_expenses_empty_list():
    """Тестирование, если передан пустой список"""
    result = card_expenses([])
    expected = []
    assert result == expected


def test_card_expenses_no_valid_data():
    """Тестирование, если нет номера карты или суммы платежа"""
    invalid_data = [
        {"Номер карты": "nan", "Сумма платежа": "nan"},
        {"Номер карты": float("nan"), "Сумма платежа": float("nan")},
    ]
    result = card_expenses(invalid_data)
    expected = []
    assert result == expected


def test_transaction_rating_by_amount(mock_data):
    """Тестирование функции, возвращающей топ-5 транзакций"""
    result = transaction_rating_by_amount(mock_data)

    expected = [
        {'date': '21.03.2019', 'amount': 190044.51, 'category': 'Переводы',
         'description': 'Перевод Кредитная карта. ТП 10.2 RUR'},
        {'date': '14.05.2019', 'amount': 42965.94, 'category': 'Другое', 'description': 'ГУП ВЦКП ЖХ'},
        {'date': '28.08.2018', 'amount': 32999.0, 'category': 'Различные товары',
         'description': 'SPb Trk Atmosfera'},
        {'date': '20.05.2021', 'amount': 8626.0, 'category': 'Бонусы',
         'description': 'Компенсация покупки'},
        {'date': '30.04.2019', 'amount': 6100.0, 'category': 'Зарплата',
         'description': 'Пополнение. ООО "ФОРТУНА". Зарплата'}
    ]
    assert result == expected


def test_transaction_rating_by_amount_empty_list():
    """Тест на случай, если передан пустой список транзакций."""
    result = transaction_rating_by_amount([])
    expected = []
    assert result == expected


def test_transaction_rating_by_amount_no_expenses(mock_data):
    """Тестирует случай, когда все транзакции являются пополнениями."""
    only_recharges = [
        {"Дата платежа": "01.01.2023", "Сумма платежа": 150, "Категория": "Пополнения", "Описание": "Пополнение"},
        {"Дата платежа": "02.01.2023", "Сумма платежа": 200, "Категория": "Пополнения", "Описание": "Пополнение"},
    ]
    result = transaction_rating_by_amount(only_recharges)
    expected = []
    assert result == expected


@patch('requests.get')
def test_exchange_rate(mock_get):
    """Тестирование функции вывода курса валют"""
    mock_response_usd = Mock()
    mock_response_usd.json.return_value = {"conversion_rates": {"RUB": 99.95}}
    mock_response_eur = Mock()
    mock_response_eur.json.return_value = {"conversion_rates": {"RUB": 105.59}}
    mock_get.side_effect = [mock_response_usd, mock_response_eur]

    result = exchange_rate(['USD', 'EUR'])
    expected = [{"currency": "USD", "rate": 99.95}, {"currency": "EUR", "rate": 105.59}]
    assert result == expected



def test_exchange_rate_no_currencies():
    """Тестирование, если передан пустой список"""
    result = exchange_rate([])
    assert result == []


@patch('requests.get')
def test_get_price_stock(mock_get):
    """Тестирование функции получения данных об акциях"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "Global Quote": {"05. price": "150.25"}
    }
    mock_get.return_value = mock_response
    stocks = {"AAPL", "MSFT"}
    expected_result = [
        {"stock": "AAPL", "price": 150.25},
        {"stock": "MSFT", "price": 150.25}, ]
    result = get_price_stock(stocks)
    assert result == expected_result


def test_get_price_stock_empty_list():
    """Тестирование, если передан пустой словарь"""
    result = get_price_stock({})
    expected = []
    assert result == expected


@patch('requests.get')
def test_get_price_stock_invalid_response(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "Global Quote": {"05. price": "invalid_price"}
    }
    mock_get.return_value = mock_response
    stocks = {"GOOGL"}
    with pytest.raises(ValueError):
        get_price_stock(stocks)


@patch("builtins.open", new_callable=mock_open, read_data='[{"currency": "USD"}, {"stock": "AAPL"}]')
def test_get_user_settings_success(mock_file):
    """Тестирование функции, возвращающей список словарей с данными об валютах и акциях"""
    result = get_user_settings("dummy_path.json")
    expected = [{"currency": "USD"}, {"stock": "AAPL"}]
    assert result == expected
    mock_file.assert_called_once_with("dummy_path.json", encoding="utf-8")


@patch("builtins.open", side_effect=FileNotFoundError)
def test_get_user_settings_file_not_found(mock_file):
    result = get_user_settings("dummy_path.json")
    expected = []
    assert result == expected
    mock_file.assert_called_once_with("dummy_path.json", encoding="utf-8")


@patch("builtins.open", new_callable=mock_open, read_data='{"currency": "USD", "stock": AAPL}')  # Некорректный JSON
def test_get_user_settings_invalid_json(mock_file):
    result = get_user_settings("dummy_path.json")
    expected = []
    assert result == expected
    mock_file.assert_called_once_with("dummy_path.json", encoding="utf-8")