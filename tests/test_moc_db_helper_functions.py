import pytest
import docker
import random
import string
import time
import mysql.connector

from contextlib import closing

import moc_db_helper_functions as mocdb


@pytest.fixture
def db_password():
    return "".join(random.choices(string.ascii_letters + string.digits, k=15))


@pytest.fixture
def db_port():
    return random.randint(10000, 30000)


@pytest.fixture
def db_container(db_password, db_port):
    client = docker.from_env()
    env = {
        "MARIADB_ROOT_PASSWORD": db_password,
        "MARIADB_USER": "test_user",
        "MARIADB_PASSWORD": db_password,
        "MARIADB_DATABASE": "testdb",
    }
    ports = {
        "3306": f"{db_port}",
    }
    container = client.containers.run(
        "docker.io/mariadb:10", environment=env, ports=ports, detach=True
    )
    yield container
    container.remove(force=True)


@pytest.fixture
def db_connection(db_container, db_password, db_port):
    while True:
        try:
            cnx = mysql.connector.connect(
                host="127.0.0.1",
                port=db_port,
                user="test_user",
                password=db_password,
                database="testdb",
            )

            cursor = cnx.cursor()
            mocdb.exec_fetchone(cursor, "select 1")

            cursor.execute(
                "create table file (script varchar(500), file_name varchar(2000), file_data longblob, primary key (script))"
            )

            with closing(cnx):
                yield cnx
                break
        except mysql.connector.errors.Error:
            time.sleep(1)


@pytest.fixture
def db_cursor(db_connection):
    with closing(db_connection.cursor()) as cursor:
        yield cursor


def test_exec_fetchone(db_cursor):
    random_number = random.randint(0, 100)
    res = mocdb.exec_fetchone(db_cursor, f"select {random_number}")
    assert res == random_number


def test_exec_fetchall(db_cursor):
    for name in ["test1", "test2"]:
        db_cursor.execute(
            "insert into file (script, file_name, file_data) values (%s, %s, %s)",
            (
                name,
                name,
                name,
            ),
        )

    res = mocdb.exec_fetchall(db_cursor, "select * from file")
    assert res == [
        ("test1", "test1", b"test1"),
        ("test2", "test2", b"test2"),
    ]
