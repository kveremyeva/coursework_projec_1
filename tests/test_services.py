import json
from unittest.mock import patch

import pandas as pd
import pytest

from config import W_JSON_SERVICES, PATH_DATA
from src.services import get_name_filter


def test_get_name_filter():
    """ Проверка корректной работы функции фильтрации имен """
    # Создаем тестовый DataFrame
    mock_df = pd.DataFrame({
        'Категория': ['Переводы', 'Переводы', 'Оплата', 'Переводы'],
        'Описание': ['Иванов И.', 'Петров П.', 'Оплата товара', 'Сидоров С.'],
        'Сумма платежа': [1000, 2000, 1500, 3000]
    })

    # Патч для имитации чтения Excel
    with patch('pandas.read_excel', return_value=mock_df):
        # Вызываем функцию
        result = get_name_filter(PATH_DATA)

        # Исправляем проверку, сравнивая JSON как объекты, а не строки
        result_obj = json.loads(result)
        expected_obj = [
            {"Описание": "Иванов И.", "Сумма платежа": 1000},
            {"Описание": "Петров П.", "Сумма платежа": 2000},
            {"Описание": "Сидоров С.", "Сумма платежа": 3000}
        ]

        # Проверяем результат
        assert result_obj == expected_obj

        # Проверяем создание файла
        with open(W_JSON_SERVICES, 'r', encoding='utf-8') as file:
            file_content = file.read()
            file_obj = json.loads(file_content)
            assert file_obj == expected_obj


def test_get_name_filter_missing_columns():
    """ Проверка обработки DataFrame без необходимых колонок """
    mock_df = pd.DataFrame({'Неправильная_категория': ['Переводы'], 'Неправильное_описание': ['Иванов И.']})
    with patch('pandas.read_excel', return_value=mock_df):
        with pytest.raises(KeyError):
            get_name_filter(PATH_DATA)


def test_get_name_filter_file_write_error():
    """ Проверка обработки ошибки при записи в файл """
    mock_df = pd.DataFrame({
        'Категория': ['Переводы'],
        'Описание': ['Иванов И.'],
        'Сумма платежа': [1000]
    })

    with patch('pandas.read_excel', return_value=mock_df):
        with patch('builtins.open', side_effect=IOError):
            with pytest.raises(IOError):
                get_name_filter(PATH_DATA)
