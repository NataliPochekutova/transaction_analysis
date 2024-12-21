import pytest
import json
from datetime import datetime

from src.services import cashback_categories

def test_cashback_categories(cashback):

    expected = json.dumps({'Супермаркеты': 24.0, 'Фастфуд': 3.0}, ensure_ascii=False)
    result = cashback_categories(cashback, 2021, 11)
    assert result == expected
