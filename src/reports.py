import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd

from config import BASE_DIR, LOGS_REPORTS, PATH_DATA

logger = logging.getLogger('reports')
logging.basicConfig(
    filename=LOGS_REPORTS,
    level=logging.INFO, filemode='w', encoding='utf-8',
    format='[%(asctime)s.%(msecs)03d] - [%(name)r] - [%(levelname)-s] - %(message)s',
)


def get_expenses_by_category_report(filename=None):
    """Декоратор для записи отчета в файл."""
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            df = func(*args, **kwargs)
            logger.info("Проверка файла")
            if filename:
                logger.info("Проверка, являются ли данные датафреймом")
                if isinstance(df, pd.DataFrame):
                    logger.info("Запись отчёта в файл")
                    with open(BASE_DIR / "logs" / filename, "w", encoding="UTF-8") as f:
                        json.dump(df.to_dict(), f, ensure_ascii=False, indent=4)
                else:
                    logger.error("Данные не являются датафреймом. В файл записаны не будут")
            else:
                logger.info("Файл будет создан на основе текущей даты")
                if isinstance(df, pd.DataFrame):
                    date = datetime.now().strftime("%d.%m.%Y")
                    logger.info("Запись отчёта в файл")
                    with open(BASE_DIR / "data" / f"{date}-report_file.json", "w", encoding="UTF-8") as f:
                        json.dump(df.to_dict(), f, ensure_ascii=False, indent=4)
                else:
                    logger.error("Данные не являются датафреймом. В файл записаны не будут")
            return df

        return inner

    return wrapper


@get_expenses_by_category_report()
def expenses_by_category(df: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""
    logger.info("Начало обработки данных")
    try:
        logger.info("Чтение данных из файла: %s", PATH_DATA)
        df = pd.read_excel(PATH_DATA)
        if 'Категория' not in df:
            logger.error("В файле отсутствует колонка 'Категория'")
            raise TypeError("В файле отсутствует колонка 'Категория'")
        if date is None:
            date = datetime.now()
        else:
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        three_months = date - timedelta(days=90)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtered_data = df[
            (df["Категория"] == category) & (df["Дата операции"] >= three_months) & (df["Дата операции"] <= date)
            ]
        if filtered_data.empty:
            logger.warning(f"Нет расходов для категории '{category}' за указанный период.")
            return pd.DataFrame(
                {
                    "category": [category],
                    "total_expenses": [0],
                    "date_from": [three_months.strftime("%d.%m.%Y")],
                    "date_to": [date.strftime("%d.%m.%Y")],
                }
            )
        total_spend = filtered_data["Сумма операции"].sum()
        report_file = pd.DataFrame(
            {
                "category": [category],
                "total_expenses": [float(round(total_spend, 2))],
                "date_from": [three_months.strftime("%d.%m.%Y")],
                "date_to": [date.strftime("%d.%m.%Y")],
            }
        )
        logger.info(f"Отчет создан для категории '{category}'")
        return report_file
    except FileNotFoundError:
        logger.error("Произошла ошибка: Файл не найден")
        return pd.DataFrame({"ERROR": ["Файл не найден"]})
    except Exception as ex:
        logger.error("Произошла ошибка: %s", ex)
        return pd.DataFrame({"ERROR": [f"Произошла ошибка: {str(ex)}"]})


if __name__ == "__main__":
    result = expenses_by_category(PATH_DATA, 'Связь')
    print(result)
