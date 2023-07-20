import json
import psycopg2
from progress.bar import IncrementalBar

from src.modules.database_manager import DBManager
from src.modules.head_hunter_api import HeadHunterAPI


def get_salary(data):
    """Возвращает величину зарплаты"""
    if not data['salary']:
        return

    if data['salary']['to']:
        salary = data['salary']['to']
        if data['salary']['currency'] != 'RUR':
            salary *= 100
    else:
        salary = data['salary']['from']
        if data['salary']['currency'] != 'RUR':
            salary *= 100

    return salary


def get_data_from_items(items):
    """Возвращает словарь вакансий с определенными значениями"""
    vacancies = []
    for vacancy in items:
        salary = get_salary(vacancy)
        if not salary:
            continue

        data_vacancies = {
            'id': vacancy['id'],
            'name': vacancy['name'].lower(),
            'city': vacancy['area']['name'],
            'salary': salary,
            'url': vacancy['alternate_url']
        }

        vacancies.append(data_vacancies)

    return vacancies


def get_data(ids_employers):
    """Возвращает данные о компаниях и их вакансиях по id компании"""

    hh_api = HeadHunterAPI()
    data = []
    bar = IncrementalBar("Сбор данных", max=len(ids_employers))

    for enum, id_employer in enumerate(ids_employers, 1):
        vacancies = []
        bar.next()

        data_employer = hh_api.get_data_employer(id_employer)
        data_vacancies = hh_api.get_data_vacancies(id_employer, 0)

        count_vacancies = data_employer['open_vacancies']

        data_employer = {
            'id': data_employer['id'],
            'name': data_employer['name'],
            'url': data_employer['site_url'],
            'hh_url': data_employer['alternate_url'],
            'count_vacancies': data_employer['open_vacancies']
        }

        if count_vacancies <= 100:
            vacancies.extend(get_data_from_items(data_vacancies['items']))

        else:
            count_current_vacancies = 0
            for i in range(0, 20):
                data_vacancies = hh_api.get_data_vacancies(id_employer, i)
                count_current_vacancies += len(data_vacancies['items'])

                vacancies.extend(get_data_from_items(data_vacancies['items']))

                if count_current_vacancies >= count_vacancies:
                    break

        data.append({
            'employer': data_employer,
            'vacancies': vacancies
        })

    bar.finish()
    print("\nДанные о работодателях и их вакансиях получены")
    return data



