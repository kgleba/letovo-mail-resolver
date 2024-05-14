import os
from enum import auto, Enum

from pymongo import MongoClient

MONGO_CLUSTER_ADDRESS = os.getenv('MONGO_CLUSTER_ADDRESS')
MONGO_ADMIN_PASSWORD = os.getenv('MONGO_ADMIN_PASSWORD')

client = MongoClient(f'mongodb+srv://admin:{MONGO_ADMIN_PASSWORD}@{MONGO_CLUSTER_ADDRESS}/')
conflicts_collection = client['teachers']['conflicts']
teachers_collection = client['teachers']['teachers']


class StatusCode(Enum):
    ENTRY_EXISTS = auto()
    ENTRY_CONFLICTS = auto()
    ENTRY_ACK = auto()
    ENTRY_NOT_ACK = auto()


def get_all_teachers() -> list[dict]:
    return list(teachers_collection.find({}))


def get_teacher_by_name(name: str) -> dict | None:
    return teachers_collection.find_one({'name': name})


def get_teacher_by_fuzzy_name(name: str) -> dict | None:
    raise NotImplementedError


def add_teacher(name: str, mail: str) -> StatusCode:
    teacher = get_teacher_by_name(name)

    if teacher is not None:
        if teacher['mail'] == mail:
            return StatusCode.ENTRY_EXISTS

        if conflicts_collection.find_one({'name': name, 'mail': mail}) is None:
            conflicts_collection.insert_one({'name': name, 'mail': mail})

        return StatusCode.ENTRY_CONFLICTS

    response = teachers_collection.insert_one({'name': name, 'mail': mail})
    return StatusCode.ENTRY_ACK if response.acknowledged else StatusCode.ENTRY_NOT_ACK


def add_teachers(teachers: dict[str, str]) -> StatusCode:
    response_status = [add_teacher(name, mail) for name, mail in teachers.items()]

    if StatusCode.ENTRY_CONFLICTS in response_status:
        return StatusCode.ENTRY_CONFLICTS

    if StatusCode.ENTRY_NOT_ACK in response_status:
        return StatusCode.ENTRY_NOT_ACK

    if StatusCode.ENTRY_EXISTS in response_status:
        return StatusCode.ENTRY_EXISTS

    return StatusCode.ENTRY_ACK
