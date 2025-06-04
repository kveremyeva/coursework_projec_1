from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import expenses_by_category


def test_expenses_by_category_success():
    """ Проверка успешного получения расходов по категории """
    mock_df = pd.DataFrame({
        'Категория': ['Еда', 'Еда', 'Транспорт', 'Еда'],
        'Дата операции': ['01.03.2025 12:00:00', '01.04.2025 12:00:00', '01.05.2025 12:00:00', '01.06.2025 12:00:00'],
        'Сумма операции': [100, 200, 150, 250]
    })

    with patch('pandas.read_excel', return_value=mock_df):
        result = expenses_by_category(mock_df, 'Еда')

        assert result['category'][0] == 'Еда'
        assert result['total_expenses'][0] == 450.00
        assert result['date_from'][0] == (datetime.now() - timedelta(days=90)).strftime("%d.%m.%Y")
        assert result['date_to'][0] == datetime.now().strftime("%d.%m.%Y")


def test_expenses_by_category_no_data():
    """ Проверка обработки отсутствия данных за период """
    mock_df = pd.DataFrame({
        'Категория': ['Еда', 'Еда', 'Транспорт', 'Еда'],
        'Дата операции': ['01.12.2024 12:00:00', '01.01.2025 12:00:00', '01.02.2025 12:00:00', '01.03.2025 12:00:00'],
        'Сумма операции': [100, 200, 150, 250]
    })

    with patch('pandas.read_excel', return_value=mock_df):
        result = expenses_by_category(mock_df, 'Еда')

        assert result['category'][0] == 'Еда'
        assert result['total_expenses'][0] == 0
        assert result['date_from'][0] == (datetime.now() - timedelta(days=90)).strftime("%d.%m.%Y")
        assert result['date_to'][0] == datetime.now().strftime("%d.%m.%Y")


def test_expenses_by_category_missing_column():
    """ Проверка обработки отсутствия колонки 'Категория' """

    mock_df = pd.DataFrame({
        'Дата операции': ['01.03.2025 12:00:00', '01.04.2025 12:00:00'],
        'Сумма операции': [100, 200]
    })

    with patch('pandas.read_excel', return_value=mock_df):
        with pytest.raises(TypeError):
            expenses_by_category(mock_df)


def test_expenses_by_category_empty_file():
    """ Проверка обработки пустого файла """
    mock_df = pd.DataFrame(columns=['Категория', 'Дата операции', 'Сумма операции'])

    with patch('pandas.read_excel', return_value=mock_df):
        result = expenses_by_category(mock_df, 'Еда')

        assert result.loc[0, 'category'] == 'Еда'
        assert result.loc[0, 'total_expenses'] == 0
        assert result.loc[0, 'date_from'] == (datetime.now() - timedelta(days=90)).strftime("%d.%m.%Y")
        assert result.loc[0, 'date_to'].split(' ')[0] == datetime.now().strftime("%d.%m.%Y").split(' ')[0]
