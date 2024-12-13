import contextlib
import typing as T
import asyncpg
from app.config import POSTGRES_DB_NAME, POSTGRES_DB_USER, POSTGRES_DB_PASSWORD, POSTGRES_DB_HOST, POSTGRES_DB_PORT

import contextlib
import typing as T
import asyncpg


class PostgresClientPool:
    def __init__(self, POSTGRES_DB_name: str = POSTGRES_DB_NAME, user: str = POSTGRES_DB_USER, password: str = POSTGRES_DB_PASSWORD, 
                 host: str = POSTGRES_DB_HOST, port: str | int = POSTGRES_DB_PORT, min_size: int = 10, max_size: int = 100):
        self.POSTGRES_DB_name = POSTGRES_DB_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.pool_min_size = min_size
        self.pool_max_size = max_size
        self.pool = None
        
    def __await__(self):
        return self._create_pool().__await__()

    async def _create_pool(self) -> None:
        self.pool = await asyncpg.create_pool(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.POSTGRES_DB_name,
            min_size=self.pool_min_size,
            max_size=self.pool_max_size,
        )

    async def close_pool(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None

    @contextlib.asynccontextmanager
    async def get_connection(self) -> T.AsyncGenerator[asyncpg.connection.Connection, None]:
        if self.pool is None:
            await self.create_pool() 
        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            await self.pool.release(conn)

    # Example function to execute a query
    async def execute_query(self, query: str, *args) -> T.Any:
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)

    # Example function to fetch data
    async def fetch(self, query: str, *args) -> T.List[T.Any]:
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)

    # Example: async def get_album(self, album_id: int) -> types.Album:
    #     async with self.get_connection() as conn:
    #         result = await conn.fetchrow(
    #             """
    #             SELECT
    #             ar.id AS artist_id,
    #             ar.name AS artist_name,
    #             al.id AS album_id,
    #             al.name AS album_name
    #             FROM albums AS al
    #             LEFT JOIN artists AS ar ON al.artist_id = ar.id
    #             WHERE al.id = $1
    #         """,
    #             album_id,
    #         )
    #         if result is None:
    #             raise AlbumNotFound()
    #         return types.Album.from_db(result)


    # async def get_albums(self) -> list[types.Album]:
    #     async with self.get_connection() as conn:
    #         result = await conn.fetch(
    #             """
    #             SELECT
    #             ar.id AS artist_id,
    #             ar.name AS artist_name,
    #             al.id AS album_id,
    #             al.name AS album_name
    #             FROM albums AS al
    #             LEFT JOIN artists AS ar ON al.artist_id = ar.id
    #         """
    #         )
    #         return [types.Album.from_db(row) for row in result]


    # async def create_album(self, album: types.AlbumIn) -> types.Album:
    #     async with self.get_connection() as conn:
    #         artist = await conn.fetchrow(
    #             """
    #             SELECT id FROM artists WHERE id = $1
    #         """,
    #             album.artist_id,
    #         )
    #         if artist is None:
    #             raise ArtistNotFound()
    #         result = await conn.fetch(
    #             """
    #             INSERT INTO albums(
    #                 name,
    #                 artist_id
    #             ) VALUES($1, $2) RETURNING id
    #         """,
    #             album.name,
    #             album.artist_id,
    #         )

    #         out = await conn.fetchrow(
    #             """
    #             SELECT
    #             ar.id AS artist_id,
    #             ar.name AS artist_name,
    #             al.id AS album_id,
    #             al.name AS album_name
    #             FROM albums AS al
    #             LEFT JOIN artists AS ar ON al.artist_id = ar.id
    #             WHERE al.id = $1
    #         """,
    #             result[0]["id"],
    #         )

    #         return types.Album.from_db(out)
