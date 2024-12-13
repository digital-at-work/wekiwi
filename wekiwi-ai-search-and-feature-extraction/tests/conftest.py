# Made open source under the GNU Affero General Public License, Version 3 (AGPL-3.0),
# by digital@work GmbH (2024). This file is part of wekiwi.
# See the LICENSE file in the project root or https://www.gnu.org/licenses/agpl-3.0.html for details.

from os import environ

import asyncpg
import pytest_asyncio

environ["ENV"] = "test"

# We have to update the ENV before importing, so ignore flake8's complaints.
# See docs for starlette config.
from app.config import POSTGRES_DB_NAME, POSTGRES_DB_USER, POSTGRES_DB_HOST, POSTGRES_DB_PORT, POSTGRES_DB_PASSWORD  # noqa: E402
from app.postgresdb.connection import get_connection  # noqa: E402
from app.postgresdb.manage_db import recreate_tables  # noqa: E402


# Create a test database before test suite, tear it down when done
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_db():
    if "test" not in POSTGRES_DB_NAME:
        raise ValueError(
            f"Expected the db name to contain 'test', stopping for safety: {POSTGRES_DB_NAME}"
        )
    sys_conn: asyncpg.Connection | None = None
    try:
        sys_conn = await asyncpg.connect(
            database="template1",
            user=POSTGRES_DB_USER,
            host=POSTGRES_DB_HOST,
            port=POSTGRES_DB_PORT,
            password=POSTGRES_DB_PASSWORD,
        )
        # Must be run separately as postgres will automatically
        # create a transaction block if there's more than one
        await sys_conn.execute(
            f"""
            DROP DATABASE IF EXISTS {POSTGRES_DB_NAME};
        """
        )
        await sys_conn.execute(
            f"""
            CREATE DATABASE {POSTGRES_DB_NAME};
        """
        )
        # async with get_connection() as conn:
        #     await recreate_tables(connection=conn)
        yield
    finally:
        if sys_conn is not None:
            await sys_conn.execute(
                f"""
                DROP DATABASE IF EXISTS {POSTGRES_DB_NAME};
            """
            )
            await sys_conn.close()


# Drop and recreate tables before and after each test
@pytest_asyncio.fixture
async def clean_db(create_db):
    async with get_connection() as conn:
        await recreate_tables(connection=conn)
    yield
