from config import PATH_DATA, W_JSON_VIEWS, W_JSON_SERVICES
from src.reports import expenses_by_category
from src.services import get_name_filter
from src.utils import read_excel
from src.views import dictionary

if __name__ == "__main__":
    data = read_excel(PATH_DATA)
    input_date = "2025-05-05 16:44:00"
    search_word = "Фастфуд"
    category = "Переводы"
    result_response = dictionary("2025-05-05 16:44:00")
    result_search = get_name_filter(data)
    result_spending = expenses_by_category(data, category, input_date)
    print("-" * 10)
    print(f"Результат работы записан в файле: {W_JSON_VIEWS}")
    print("-" * 10)
    print(f"Результат работы записан в файле: {W_JSON_SERVICES}")
    print("-" * 10)
    print(f"Результат работы указан ниже: \n{result_spending}")