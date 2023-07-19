import psycopg2


class DBManager:
    """Класс для работы с базой данных Postgresql"""

    def __init__(self, database_name, params):
        self.database_name = database_name
        self.params = params
        self.create_database(self.database_name, self.params)

    @staticmethod
    def create_database(dbname, params):
        """Создание базы данных и таблиц для хранения данных о работодателе и его вакансиях"""
        conn = psycopg2.connect(dbname='postgres', **params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{dbname}' -- ← изменить на свое название БД
        AND pid <> pg_backend_pid();
        """)

        cur.execute(f'DROP DATABASE IF EXISTS {dbname}')
        cur.execute(f'CREATE DATABASE {dbname}')

        conn.close()

        conn = psycopg2.connect(dbname=dbname, **params)

        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE employers (
                    employer_id INT PRIMARY KEY,
                    name_employer VARCHAR NOT NULL,
                    employer_url TEXT,
                    employer_hh_url TEXT,
                    count_vacancies INTEGER
                )
            """)

        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE vacancies (
                    vacancy_id INT PRIMARY KEY,
                    employer_id INT REFERENCES employers(employer_id),
                    name_vacancy VARCHAR NOT NULL,
                    city VARCHAR,
                    salary REAL,
                    vacancy_url TEXT
                )
            """)

        conn.commit()
        conn.close()
        print('База данных с таблицами создана')

    def get_companies_and_vacancies_count(self):
        """Возвращает список всех компаний и количество сохраненных вакансий у каждой компании,
         содержащих уровень зарплаты"""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute("""
                SELECT employers.name_employer, count(vacancies.vacancy_id) 
                FROM vacancies
                JOIN employers using(employer_id)
                GROUP BY employers.name_employer
            """)
            data = cur.fetchall()
        conn.commit()
        conn.close()
        return data

    def get_all_vacancies(self):
        """Возвращает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute("""
                        SELECT employers.name_employer, vacancies.name_vacancy, vacancies.salary, vacancies.vacancy_url
                        FROM vacancies
                        JOIN employers using(employer_id)
                        ORDER BY vacancies.salary
                    """)
            data = cur.fetchall()
        conn.commit()
        conn.close()
        return data

    def get_avg_salary(self):
        """Возвращает среднюю зарплату по вакансиям"""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute("""
                        SELECT AVG(salary)::INTEGER AS average_salary FROM vacancies
                        """)
            data = cur.fetchall()
        conn.commit()
        conn.close()
        return data

    def get_vacancies_with_higher_salary(self):
        """Возвращает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute("""
                        SELECT * FROM vacancies
                        WHERE salary > (SELECT avg(salary) FROM vacancies)
                        ORDER BY salary
                        """)
            data = cur.fetchall()
        conn.commit()
        conn.close()
        return data

    def get_vacancies_with_keyword(self, keyword):
        """Возвращает список всех вакансий, в названии которых содержатся переданное в метод слово"""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(f"""
                        SELECT * FROM vacancies
                        WHERE name_vacancy LIKE '%{keyword.lower()}%'
                        """)
            data = cur.fetchall()
        conn.commit()
        conn.close()
        return data

    def __repr__(self):
        return f"{__class__.__name__}('{self.database_name}', '{self.params}')"
