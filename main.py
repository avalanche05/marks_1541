import os

import requests
from bs4 import BeautifulSoup
import csv

TABLE = '/table'
LOGIN_URL = 'https://contest.nlogn.info/api/user/authenticate/sign-in'
HOST = 'https://contest.nlogn.info'
session = requests.Session()
CLASSES = dict()
STARS = []


# Здесь можно выставить политику оценивания
def get_mark(solved_task: int, max_task: int) -> int:
    """
    :param solved_task: количество решённых задач учеником
    :param max_task: количество задач в контесте
    :return: функция возвращает оценку ученика
    """

    if solved_task == max_task:
        return 5
    if solved_task == max_task - 1:
        return 4
    if solved_task == 0:
        return 2
    return 3


def get_mark_stars(solved_task: int, max_task: int) -> int:
    """
    :param solved_task: количество решённых задач учеником
    :param max_task: количество задач в контесте
    :return: функция возвращает оценку ученика
    """

    if solved_task >= 2:
        return 5
    if solved_task == 1:
        return 4
    return -1


def parse_classes():
    class_files = os.listdir('classes')
    for class_file in class_files:
        with open('classes/' + class_file) as csvfile:
            reader = csv.reader(csvfile)
            class_name = class_file.split('.')[0]
            students = list(map(lambda x: x[0], reader))
            CLASSES[class_name] = students


def auth(login: str, password: str):
    body = {
        'login': login,
        'password': password
    }

    response = session.post(LOGIN_URL, data=body)


def print_table(contest_id: str):
    params = {
        'contestId': contest_id,
        'count': 100,
        'offset': 0,
        'showInTimeMs': 'Infinity'
    }
    response = session.get(HOST + f'/api/contest/{contest_id}/table2', params=params)

    raw = response.json()
    tasks_count = len(raw['header'])

    marks = []

    for user in raw['rows']:
        user_name = user['user']['fullName']
        solved_tasks_count = int(user['acceptedSolutions'])
        if contest_id in STARS:
            mark = get_mark_stars(solved_tasks_count, tasks_count)
        else:
            mark = get_mark(solved_tasks_count, tasks_count)

        marks.append((user_name, mark))

    print('ID контеста:', contest_id, '\n')

    for class_name, students in CLASSES.items():
        print('Класс:', class_name, '\n')
        for student in students:
            mark = -1
            student_set = set([str(t).lower() for t in student.split()])
            for contestant, contestant_mark in marks:
                contestant_set = set([str(t).lower() for t in contestant.split()])

                if student_set == contestant_set:
                    mark = contestant_mark

            print(student, mark)
        print('-----------------')
    print()
    print('********************************')
    print()


def contests():
    with open('contests.csv') as csvfile:
        reader = csv.reader(csvfile)

        for contest in reader:
            if '*' in contest[0]:
                contest[0] = contest[0].replace('*', '')
                STARS.append(contest[0])
            link = contest[0]
            print_table(link)


def main():
    parse_classes()
    auth('l.2022', 'lshp2022')
    contests()


if __name__ == '__main__':
    main()
