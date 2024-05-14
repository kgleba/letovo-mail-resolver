import os

from pymongo import MongoClient

MONGO_CLUSTER_ADDRESS = os.getenv('MONGO_CLUSTER_ADDRESS')
MONGO_ADMIN_PASSWORD = os.getenv('MONGO_ADMIN_PASSWORD')

client = MongoClient(f'mongodb+srv://admin:{MONGO_ADMIN_PASSWORD}@{MONGO_CLUSTER_ADDRESS}/')
conflicts_collection = client['teachers']['conflicts']
teachers_collection = client['teachers']['teachers']


def get_all_teachers() -> list[dict]:
    return list(teachers_collection.find({}))


def get_teacher_by_name(name: str) -> dict | None:
    return teachers_collection.find_one({'name': name})


def get_teacher_by_fuzzy_name(name: str) -> dict | None:
    raise NotImplementedError


def add_teacher(name: str, mail: str) -> bool:
    teacher = get_teacher_by_name(name)

    if teacher is not None:
        if teacher['mail'] == mail:
            return True

        conflicts_collection.insert_one({'name': name, 'mail': mail})
        return False

    response = teachers_collection.insert_one({'name': name, 'mail': mail})
    return response.acknowledged


def add_teachers(teachers: dict[str, str]) -> bool:
    response_status = [add_teacher(name, mail) for name, mail in teachers.items()]
    return all(response_status)
