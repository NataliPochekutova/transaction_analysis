import json
import pandas as pd
import pytest
from src.reports import spending_by_category


@pytest.fixture
def transactions():
    return pd.DataFrame({
        "Категория": ["Еда", "Транспорт", "Еда", "Досуг", "Еда"],
        "Дата платежа": ["01.01.2023", "15.02.2023", "20.03.2023", "nan", "25.03.2023"],
        "Сумма платежа": [1000, 1500, 2000, 500, 3000]
    })


def test_no_date(transactions):
    result = spending_by_category(transactions, category="Еда", date=None)
    result_list = json.loads(result)

    assert result_list[0]["amount"] == 2000
    assert result_list[1]["amount"] == 3000
    assert result_list[2]["amount"] == 1000


def test_with_date(transactions):
    result = spending_by_category(transactions, category="Еда", date="20.03.2023")
    result_list = json.loads(result)

    assert result_list[0]["amount"] == 2000
    assert result_list[1]["amount"] == 1000


def test_no_transactions_in_category(transactions):
    result = spending_by_category(transactions, category="Недвижимость", date=None)
    result_list = json.loads(result)

    assert len(result_list) == 0



