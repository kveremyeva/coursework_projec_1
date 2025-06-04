import json
import logging
import os
from datetime import datetime
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

from config import JSON_DATA, LOGS_UTILS, PATH_DATA

load_dotenv(r'..\.env')

API_KEY = os.getenv('API_KEY')

headers = {"apikey": "API_KEY"}


logger = logging.getLogger('utils')
logging.basicConfig(
    filename=LOGS_UTILS,
    level=logging.INFO, filemode='w', encoding='utf-8',
    format='[%(asctime)s.%(msecs)03d] - [%(name)r] - [%(levelname)-7s] - %(message)s',
)


def read_excel(path: str) -> pd.DataFrame:
    """ Функция чтения Excel файла"""
    try:
        logger.info("Запускается чтение файла")
        df = pd.read_excel(path)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        return df
    except Exception as ex:
        logger.error("Ошибка загрузки %s", ex)
        return {}


def data_time(date_str: str) -> str:
    """ Функция для приветсвия клиента по текущему времени"""
    logger.info(f"Запуск функции {data_time}")
    try:
        logger.info("Получение даты")
        now = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.error("Неверный формат даты, используется текущая дата")
        now = datetime.now()
    if 6 <= now.hour < 12:
        return "Доброе утро"
    elif 12 <= now.hour < 18:
        return "Добрый день"
    elif 18 <= now.hour < 24:
        return "Добрый вечер"
    elif 0 <= now.hour < 6:
        return "Доброй ночи"
    return None


def get_operations_with_range(date: str) -> pd.DataFrame:
    """ Функция получения операций за период с начала месяца по введенныю дату"""
    logger.info(f"Запуск функции {get_operations_with_range}")
    try:
        logger.info("Получение даты")
        date_start = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-01 00:00:00")
        df = read_excel(PATH_DATA)
        filter_operations = df[(df["Дата операции"] >= date_start) & (df["Дата операции"] <= date)]
        return filter_operations
    except ValueError:
        logger.error("Неверный формат даты")
        return "Неверный формат даты"


def summ_by_category(transactions: pd.DataFrame) -> list[dict]:
    """ Считаем сумму платежа и кешбека по каждой карте"""
    logger.info(f"Запуск функции {summ_by_category}")
    try:
        transactions = transactions[(transactions["Сумма платежа"] < 0) & (transactions["Статус"] == "OK")]
        transactions = transactions[["Сумма платежа", "Номер карты",
                                     "Кэшбэк"]].groupby("Номер карты").sum().reset_index()
        transactions['last_digits'] = transactions.pop("Номер карты")
        transactions['total_spent'] = transactions.pop("Сумма платежа")
        transactions['cashback'] = transactions.pop("Кэшбэк")
        cards = transactions.to_dict(orient="records")
        logger.info("Получение данных")
        return cards
    except Exception as ex:
        logging.error("Ошибка фильтрации: %s. Возврат данных", ex)
        return transactions


def get_top_transactions(df: pd.DataFrame) -> list[dict]:
    """ Топ 5 транзакций по сумме платежа"""
    result = []
    df = read_excel(PATH_DATA)
    logger.info(f"Запуск функции {get_top_transactions}")
    try:
        logger.info("Получение данных")
        top_transactions = df.sort_values(by="Сумма платежа", ascending=False).head(5).reset_index().to_dict(
            orient="records")
        for transaction in top_transactions:
            date = transaction['Дата операции'].strftime('%d.%m.%Y')
            amount = float(transaction['Сумма операции'])
            category = transaction['Категория']
            description = transaction['Описание']
            result.append({
                "date": date,
                "amount": amount,
                "category": category,
                "description": description
            })
        logger.info("Запись полученных транзакций")
        return result
    except Exception as ex:
        logging.error("Ошибка получения данных: %s", ex)
        return []


def get_currency(currency: list, api_key=None) -> Any:
    """ Функция берет данные из JSON файла курс валют через API запрос"""
    logger.info(f"Запуск функции {get_currency}")
    results = []
    try:
        logger.info(f"Чтение данных из файла: {JSON_DATA}")
        with open(JSON_DATA, encoding='utf-8') as file:
            currency_json = json.load(file)
            currency_symbol = currency_json['user_currencies']
            logger.info("Обращение к Api")
            for curr in currency_symbol:
                url = "https://www.cbr-xml-daily.ru/daily_json.js"
                response = requests.request("GET", url, headers=headers)
                status_code = response.status_code
                logger.info("Проверка статус-ответа")
                if status_code == 200:
                    result = response.json()['Valute'][curr]['Value']
                    logger.info(f"Запрос данных по: {curr}")
                    results.append((float(result)))
                    logger.info("Обращение успешно")
                    formatted_rates = [
                        {"currency": c, "rate": r}
                        for c, r in zip(currency_symbol, results)
                    ]
                else:
                    logger.error(f"Не успешный запрос, код ошибки: {status_code}")
                    return f"Не успешный запрос, код ошибки: {status_code}"
            return formatted_rates
    except Exception as ex:
        logger.error(f"Ошибка получения курса валют: {ex}")
        return formatted_rates


def get_stocks(stock: list) -> Any:
    logger.info(f"Запуск функции {get_stocks}")
    """ Функция берет данные из JSON файла и возвращает акции через API"""
    try:
        results = []
        logger.info(f"Чтение данных из файла: {JSON_DATA}")
        with open(JSON_DATA, encoding='utf-8') as file:
            stocks_json = json.load(file)
            stock_symbol = stocks_json['user_stocks']
            logger.info("Обращение к Api")
            for stock in stock_symbol:
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY}"
                response = requests.request("GET", url, headers=headers)
                status_code = response.status_code
                logger.info("Проверка статус-ответа")
                if status_code == 200:
                    result = response.json()["Global Quote"]["02. open"]
                    logger.info(f"Запрос данных по: {stock}")
                    results.append((float(result)))
                    logger.info("Обращение успешно")
                    formated_stocks = [
                        {"stock": s, "price": p}
                        for s, p in zip(stock_symbol, results)
                    ]
                else:
                    logger.error(f"Не успешный запрос, код ошибки: {status_code}")
                    return f"Не успешный запрос, код ошибки: {status_code}"
            return formated_stocks
    except Exception as ex:
        logger.error(f"Ошибка получения цены для {stock}: {ex}")
        return results
