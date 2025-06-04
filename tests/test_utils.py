import json
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest

from src.utils import data_time, get_currency, get_stocks, read_excel


# Тесты для функции get_greeting
@pytest.mark.parametrize(
    "test_inp, expected",
    [
        ("2023-05-15 08:30:00", "Доброе утро"),
        ("2023-05-15 14:15:00", "Добрый день"),
        ("2023-05-15 19:45:00", "Добрый вечер"),
        ("2023-05-15 03:20:00", "Доброй ночи"),
        ("2023-05-15 05:00:00", "Доброй ночи"),
        ("2023-05-15 11:59:59", "Доброе утро"),
        ("2023-05-15 12:00:00", "Добрый день"),
        ("2023-05-15 17:59:59", "Добрый день"),
        ("2023-05-15 18:00:00", "Добрый вечер"),
        ("2023-05-15 23:59:59", "Добрый вечер"),
        ("2023-05-15 00:00:00", "Доброй ночи"),
        ("2023-05-15 04:59:59", "Доброй ночи"),
    ],
)
def test_get_greeting(test_inp: str, expected: str) -> None:
    assert data_time(test_inp) == expected


@patch("requests.get")
def test_successful_response_with_valid_currencies(mock_get) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Valute": {"USD": {"Value": 78.5025}, "EUR": {"Value": 89.3108}}
    }
    mock_get.return_value = mock_response

    currencies = ["USD", "EUR"]
    result = get_currency(currencies)

    assert len(result) == 2
    assert {"currency": "USD", "rate": 78.5025} == result[0]
    assert {"currency": "EUR", "rate": 89.3108} == result[1]


def test_empty_excel_file():
    """ Проверка обработки пустого Excel файла """
    empty_df = pd.DataFrame()
    with patch('pandas.read_excel') as mock_read_excel:
        mock_read_excel.return_value = empty_df
        result = read_excel('any_path')

        assert result == {}
        mock_read_excel.assert_called_once_with('any_path')


def test_missing_date_column():
    """ Проверка обработки файла без колонки 'Дата операции' """
    empty_df = pd.DataFrame({'Другой_столбец': [1, 2, 3]})
    with patch('pandas.read_excel') as mock_read_excel:
        mock_read_excel.return_value = empty_df

        assert read_excel('any_path') == {}


def test_incorrect_date_format():
    """ Проверка обработки некорректного формата даты """
    incorrect_df = pd.DataFrame({'Дата операции': ['не_дата', 'еще_не_дата']})
    with patch('pandas.read_excel') as mock_read_excel:
        mock_read_excel.return_value = incorrect_df

        assert read_excel('any_path') == {}


def test_get_stocks_success():
    """ Проверка успешного получения данных по акциям """
    mock_json = {
        "user_stocks": ["AAPL", "GOOGL"]
    }

    mock_response = {
        "Global Quote": {
            "02. open": "150.00"
        }
    }

    with patch('builtins.open', mock_open(read_data=json.dumps(mock_json))):
        with patch('requests.request') as mock_requests:
            mock_requests.return_value = Mock(
                status_code=200,
                json=lambda: mock_response
            )
            result = get_stocks(["AAPL", "GOOGL"])

            assert result == [
                {"stock": "AAPL", "price": 150.00},
                {"stock": "GOOGL", "price": 150.00}
            ]


def test_get_stocks_file_not_found():
    """ Проверка обработки отсутствия файла """
    with patch('builtins.open', side_effect=FileNotFoundError):
        result = get_stocks(["AAPL"])
        assert result == []


def test_get_stocks_invalid_json():
    """ Проверка обработки некорректного JSON файла """
    with patch('builtins.open', mock_open(read_data="некорректный JSON")):
        result = get_stocks(["AAPL"])
        assert result == []


def test_get_stocks_api_error():
    """ Проверка обработки ошибки API """
    mock_json = {
        "user_stocks": ["AAPL"]
    }

    with patch('builtins.open', mock_open(read_data=json.dumps(mock_json))):
        with patch('requests.request') as mock_requests:
            mock_requests.return_value = Mock(
                status_code=500
            )

            result = get_stocks(["AAPL"])
            assert result == "Не успешный запрос, код ошибки: 500"


def test_get_stocks_invalid_api_key():
    """ Проверка обработки некорректного API ключа """
    mock_json = {
        "user_stocks": ["AAPL"]
    }

    with patch('builtins.open', mock_open(read_data=json.dumps(mock_json))):
        with patch('requests.request') as mock_requests:
            mock_requests.return_value = Mock(
                status_code=401
            )

            result = get_stocks(["AAPL"])
            assert result == "Не успешный запрос, код ошибки: 401"


def test_get_stocks_missing_api_key():
    """ Проверка обработки отсутствия ключа в ответе API """
    mock_json = {
        "user_stocks": ["AAPL"]
    }

    with patch('builtins.open', mock_open(read_data=json.dumps(mock_json))):
        with patch('requests.request') as mock_requests:
            mock_requests.return_value = Mock(
                status_code=200,
                json=lambda: {}
            )

            result = get_stocks(["AAPL"])
            assert result == []
