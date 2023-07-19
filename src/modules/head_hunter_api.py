import requests
import random
from progress.bar import IncrementalBar
from time import sleep


class HeadHunterAPI:
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        # ссылка для подключения
        self.url = 'https://api.hh.ru/vacancies'

    @staticmethod
    def get_data_from_url_with_params(url, params):
        """Возвращает данные по url с использованием параметров"""
        try:
            req = requests.get(url, params)
            data = req.json()
            req.close()
            sleep(0.5)
            return data
        except requests.exceptions.ConnectionError:
            return

    def get_data_vacancies(self, id_, page):
        """Возвращает данные о вакансиях компании по её id"""
        params = {
            'employer_id': id_,
            'page': page,
            'per_page': 100
        }
        data = self.get_data_from_url_with_params(self.url, params)
        return data

    def get_data_employer(self, id_employer):
        """Возвращает данные о компании по её id"""
        url = f'https://api.hh.ru/employers/{id_employer}'
        data = self.get_data_from_url_with_params(url, {})
        return data

    def get_id_random_ten_employers(self):
        """Возвращает список 10 случайных компаний, где количество вакансий в диапазоне от 50 до 2000"""
        print('Начат поиск работодателей, это займет некоторое время...')
        params = {
            'text': 'python разработчик',
            'area': 1,
            'page': 1,
            'per_page': 100
        }

        data = self.get_data_from_url_with_params(self.url, params)

        if not data:
            return

        bar = IncrementalBar("Поиск работодателей", max=len(data['items']))
        id_employers = []
        for item in data['items']:
            bar.next()
            try:
                id_ = item['employer']['id']
                data_employer = self.get_data_employer(id_)
                if 50 <= data_employer['open_vacancies'] <= 2000:
                    id_employers.append(id_)
            except KeyError:
                continue
        random.shuffle(id_employers)

        bar.finish()
        print('Список из 10 случайных компаний составлен.')
        return id_employers[:10]
