import json
import logging

from config import LOGS_VIEWS, W_JSON_VIEWS
from src.utils import (data_time, get_currency, get_operations_with_range, get_stocks, get_top_transactions,
                       summ_by_category)

logger = logging.getLogger('views')
logging.basicConfig(
    filename=LOGS_VIEWS,
    level=logging.INFO, filemode='w', encoding='utf-8',
    format='[%(asctime)s.%(msecs)03d] - [%(name)r] - [%(levelname)-7s] - %(message)s',
)


def dictionary(transactions):
    """ Функция записи данных в JSON файл"""
    logger.info("Запуск функции для создания JSON файла")
    my_dict = {}
    my_dict['greeting'] = data_time("2025-05-05 16:44:00")
    my_dict['cards'] = summ_by_category(get_operations_with_range("2025-05-31 12:12:12"))
    my_dict['top_transactions'] = get_top_transactions(transactions)
    my_dict['stock_prices'] = get_currency("")
    my_dict['currency_rates'] = get_stocks("")
    logger.info(f"Открытие и запись в {W_JSON_VIEWS}")
    with open(W_JSON_VIEWS, 'w', encoding='utf-8') as file:
        json.dump(my_dict, file, ensure_ascii=False, indent=4)
    return my_dict


if __name__ == "__main__":
    input_date = "2025-05-05 16:44:00"
    response = dictionary(input_date)
