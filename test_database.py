import pytest
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from pytest_docker import docker_compose, Container

Base = declarative_base()

class TestTable(Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))

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
    engine = create_engine(
        postgres_container.get_url("postgres", 5432),
        poolclass=QueuePool,  # Use QueuePool for better handling of bursts of connections
        pool_size=50,  # Increase pool size to handle more concurrent connections
        max_overflow=100,  # Allow for more temporary connections during peaks
        echo=False,  # Set to True for debugging SQL queries
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

# Test case to insert and validate data
def test_insert_data(database):
    new_records = [TestTable(name=f"John Doe {i}") for i in range(1000)]  # Insert 1000 records
    database.add_all(new_records)
    database.commit()

    results = database.query(TestTable).filter(TestTable.name.like("John Doe%")).all()
    assert len(results) == 1000

# Test case to update and validate data
def test_update_data(database):
    new_records = [TestTable(name=f"Jane Doe {i}") for i in range(1000)]
    database.add_all(new_records)
    database.commit()

    for record in new_records:
        record.name = "Updated Name"
    database.commit()

    results = database.query(TestTable).filter(TestTable.name == "Updated Name").all()
    assert len(results) == 1000

# Test case to delete data
def test_delete_data(database):
    new_records = [TestTable(name=f"Delete Me {i}") for i in range(1000)]
    database.add_all(new_records)
    database.commit()

    for record in new_records:
        database.delete(record)
    database.commit()

    count = database.query(TestTable).count()
    assert count == 0

# Test case to query multiple records
def test_query_multiple_records(database):
    records_to_insert = [TestTable(name=f"Record {i}") for i in range(1000)]
    database.add_all(records_to_insert)
    database.commit()

    results = database.query(TestTable).filter(TestTable.name.like("Record%")).all()
    assert len(results) == 1000

# Test case for handling edge cases (empty table)
def test_empty_table(database):
    result = database.query(TestTable).filter(TestTable.name == "Nonexistent").first()
    assert result is None

# Test case to test transaction rollback
def test_transaction_rollback(database):
    new_record = TestTable(name="To Be Rolled Back")
    database.add(new_record)
    database.commit()

    # Intentionally raise an exception to trigger a rollback
    with pytest.raises(Exception):
        with database.begin_nested():
            # Modify the record
            new_record.name = "Modified Name"
            database.commit()
            raise Exception("Intentional exception")

    # Check that the changes were rolled back
    result = database.query(TestTable).filter(TestTable.id == new_record.id).first()
    assert result.name == "To Be Rolled Back"
