import pytest
import docker
import random
import string
import time
import mysql.connector

from contextlib import closing


@pytest.fixture(scope="session")
def db_password():
    return "".join(random.choices(string.ascii_letters + string.digits, k=15))


@pytest.fixture(scope="session")
def db_port():
    return random.randint(10000, 30000)


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
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
            with closing(cursor):
                cursor.execute("select 1")
                cursor.fetchone()
            break
        except mysql.connector.errors.Error:
            time.sleep(1)

    with closing(cnx):
        yield cnx


@pytest.fixture
def db_cursor(db_connection):
    with closing(db_connection.cursor()) as cursor:
        yield cursor
