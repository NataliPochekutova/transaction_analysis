import json
import pandas as pd
import pytest
from src.reports import spending_by_category


@pytest.fixture
def transactions():
    return pd.DataFrame({
        "Категория": ["Еда", "Транспорт", "Еда", "Досуг", "Еда"],
        "Дата платежа": ["10.10.2024", "15.11.2024", "20.12.2024", "nan", "23.12.2024"],
        "Сумма платежа": [1000, 1500, 2000, 500, 3000]
    })


def test_no_date(transactions):
    result = spending_by_category(transactions, category="Еда", date=None)
    result_list = json.loads(result)

    assert result_list[0]["amount"] == 1000
    assert result_list[1]["amount"] == 2000
    assert result_list[2]["amount"] == 3000


def test_with_date(transactions):
    result = spending_by_category(transactions, category="Еда", date="20.12.2024")
    result_list = json.loads(result)

    assert result_list[0]["amount"] == 1000
    assert result_list[1]["amount"] == 2000


def test_no_transactions_in_category(transactions):
    result = spending_by_category(transactions, category="Недвижимость", date=None)
    result_list = json.loads(result)

    assert len(result_list) == 0
