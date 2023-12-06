import pytest
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import text
from pytest_docker import docker_compose, Container

# Define the Docker Compose configuration for PostgreSQL
docker_compose_file = '''
version: '3.8'
services:
  postgres:
    image: postgres:latest
    environment:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpassword
      POSTGRES_DB: testdb
'''

# Fixture to start and stop the PostgreSQL container
@pytest.fixture(scope="session")
def postgres_container(docker_services):
    with docker_compose(docker_services, docker_compose_file) as _:
        yield Container.get("postgres")

# Fixture to create a database connection and initialize the schema
@pytest.fixture
def database(postgres_container):
    conn = psycopg2.connect(
        host=postgres_container.get_url("postgres", 5432),
        user="testuser",
        password="testpassword",
        database="testdb",
    )

    # Create a table for testing
    with conn.cursor() as cursor:
        try:
            cursor.execute("CREATE TABLE test_table (id SERIAL PRIMARY KEY, name VARCHAR(255))")
            conn.commit()
        except ProgrammingError as e:
            # Table already exists
            pass

    yield conn

    # Clean up
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS test_table")
        conn.commit()
    conn.close()

# Test case to insert and validate data
def test_insert_data(database):
    with database.cursor() as cursor:
        cursor.execute("INSERT INTO test_table (name) VALUES (%s)", ("John Doe",))
        database.commit()

    with database.cursor() as cursor:
        cursor.execute("SELECT name FROM test_table WHERE id = 1")
        result = cursor.fetchone()
        assert result[0] == "John Doe"

# Test case to update and validate data
def test_update_data(database):
    with database.cursor() as cursor:
        cursor.execute("INSERT INTO test_table (name) VALUES (%s)", ("Jane Doe",))
        database.commit()

    with database.cursor() as cursor:
        cursor.execute("UPDATE test_table SET name = %s WHERE id = 1", ("Updated Name",))
        database.commit()

    with database.cursor() as cursor:
        cursor.execute("SELECT name FROM test_table WHERE id = 1")
        result = cursor.fetchone()
        assert result[0] == "Updated Name"

# Test case to delete data
def test_delete_data(database):
    with database.cursor() as cursor:
        cursor.execute("INSERT INTO test_table (name) VALUES (%s)", ("Delete Me",))
        database.commit()

    with database.cursor() as cursor:
        cursor.execute("DELETE FROM test_table WHERE id = 1")
        database.commit()

    with database.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM test_table")
        result = cursor.fetchone()
        assert result[0] == 0
