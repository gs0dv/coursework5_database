SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '{dbname}' -- ← изменить на свое название БД
AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS {dbname};

CREATE DATABASE {dbname};

CREATE TABLE employers (
    employer_id INT PRIMARY KEY,
    name_employer VARCHAR NOT NULL,
    employer_url TEXT,
    employer_hh_url TEXT,
    count_vacancies INTEGER
);

CREATE TABLE vacancies (
    vacancy_id INT PRIMARY KEY,
    employer_id INT REFERENCES employers(employer_id),
    name_vacancy VARCHAR NOT NULL,
    city VARCHAR,
    salary REAL,
    vacancy_url TEXT
);

SELECT employers.name_employer, count(vacancies.vacancy_id)
FROM vacancies
JOIN employers using(employer_id)
GROUP BY employers.name_employer;

SELECT employers.name_employer, vacancies.name_vacancy, vacancies.salary, vacancies.vacancy_url
FROM vacancies
JOIN employers using(employer_id)
ORDER BY vacancies.salary;

SELECT AVG(salary)::INTEGER AS average_salary FROM vacancies;

SELECT * FROM vacancies
WHERE salary > (SELECT avg(salary) FROM vacancies)
ORDER BY salary;

SELECT * FROM vacancies
WHERE name_vacancy LIKE '%{keyword.lower()}%';

INSERT INTO employers (employer_id, name_employer, employer_url, employer_hh_url, count_vacancies)
VALUES (%s, %s, %s, %s, %s)
RETURNING employer_id, (
      employer_data['id'],
      employer_data['name'],
      employer_data['url'],
      employer_data['hh_url'],
      employer_data['count_vacancies'])

INSERT INTO vacancies (vacancy_id, employer_id, name_vacancy, city, salary, vacancy_url)
VALUES (%s, %s, %s, %s, %s, %s), (
                      vacancy['id'],
                      employer_id,
                      vacancy['name'],
                      vacancy['city'],
                      vacancy['salary'],
                      vacancy['url'],)