import logging
import re

import pandas as pd

from config import LOGS_SERVICES, PATH_DATA, W_JSON_SERVICES

logger = logging.getLogger('services')
logging.basicConfig(
    filename=LOGS_SERVICES,
    level=logging.INFO, filemode='w', encoding='utf-8',
    format='[%(asctime)s.%(msecs)03d] - [%(name)r] - [%(levelname)-7s] - %(message)s',
)


def get_name_filter(df: pd.DataFrame) -> list[dict]:
    """ Функция для поиска переводов физическим лицам"""
    try:
        logger.info("Начало обработки данных")
        logger.info(f"Чтение данных из файла: {PATH_DATA}")
        df = pd.read_excel(PATH_DATA)
        logger.info("Создание паттерна для поиска имен")
        name_pattern = re.compile(r'\b[А-Я][а-я]+\s[А-Я]\.')
        logger.info("Фильтрация транзакций")
        filtered_df = df[(df['Категория'] == 'Переводы') & (df['Описание'].str.contains(name_pattern))]
        filtered_df = filtered_df[['Описание', 'Сумма платежа']]
        logger.info(f"Найдено записей: {len(filtered_df)}")
        logger.info("Конвертация данных в JSON формат")
        json_data = filtered_df.to_json(orient='records', force_ascii=False, indent=2)
        logger.info(f"Сохранение JSON в файл: {W_JSON_SERVICES}")
        with open(W_JSON_SERVICES, 'w', encoding='utf-8') as file:
            file.write(json_data)
        logger.info("Обработка завершена успешно")
        return json_data
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        raise


