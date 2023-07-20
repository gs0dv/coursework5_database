from src.modules.database_manager import DBManager
from src.modules.head_hunter_api import HeadHunterAPI
from src.utils.utils import get_data


def main():
    """Точка входа программы"""

    # экземпляр класса HH API
    hh_api = HeadHunterAPI()

    # параметры для подключения
    params = {
        'host': 'localhost',
        'user': 'postgres',
        'password': 12345,
        'port': 5432
    }
    # имя базы данных
    db_name = 'hh_ru_database'

    # экземпляр для подключения, создания и работы с базой данных Postgres
    db_manager = DBManager(db_name, params)

    # получение 10 случайных компаний, у которых число вакансий в диапазоне от 50 до 2000
    id_random_ten_employers = hh_api.get_id_random_ten_employers()

    if not id_random_ten_employers:
        print('Не удалось подключиться к API')
        exit()

    # получение данных о выбранных компаниях и их вакансиях
    data = get_data(id_random_ten_employers)

    # сохранение данных в базу Postgres
    db_manager.save_data_to_database(data, db_name, params)
    print(" ")

    filtered_data = db_manager.get_companies_and_vacancies_count()
    print('Список всех компаний и количество сохраненных вакансий у каждой компании, содержащих уровень зарплаты')
    for item in filtered_data:
        print(item)

    filtered_data = db_manager.get_all_vacancies()
    print('\nСписок всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию')
    for item in filtered_data:
        print(item)

    filtered_data = db_manager.get_avg_salary()
    print('\nСредняя зарплата по вакансиям')
    for item in filtered_data:
        print(item)

    filtered_data = db_manager.get_vacancies_with_higher_salary()
    print('\nСписок всех вакансий, у которых зарплата выше средней по всем вакансиям')
    for item in filtered_data:
        print(item)

    filtered_data = db_manager.get_vacancies_with_keyword('Python')
    print('\nСписок всех вакансий, в названии которых содержатся переданное в метод слово')
    for item in filtered_data:
        print(item)


if __name__ == '__main__':
    main()
