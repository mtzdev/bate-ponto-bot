import aiosqlite

class Database:
    def __init__(self, db_connection):
        self.connector = db_connection

    async def get_user_time(self, user_id: int):
        async with aiosqlite.connect(self.connector) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT * FROM tempo_semanal WHERE user_id = ?', (user_id, ))
                return await cursor.fetchone()

    async def get_ranking(self, amount: int = 10):
        async with aiosqlite.connect(self.connector) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT * FROM tempo_semanal ORDER BY tempo_total DESC LIMIT ?', (amount, ))
                return await cursor.fetchall()

    async def add_time(self, user_id: int, seconds: int):
        async with aiosqlite.connect(self.connector) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('INSERT OR IGNORE INTO tempo_semanal(user_id) VALUES (?)', (user_id, ))  # Cria a conta caso não exista
                await cursor.execute('UPDATE tempo_semanal SET tempo_total = tempo_total + :seconds WHERE user_id = :user', {'seconds': seconds, 'user': user_id})
                await conn.commit()
                return True

    async def set_time(self, user_id: int, seconds: int):
        async with aiosqlite.connect(self.connector) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('INSERT OR IGNORE INTO tempo_semanal(user_id) VALUES (?)', (user_id, ))  # Cria a conta caso não exista
                await cursor.execute('UPDATE tempo_semanal SET tempo_total = :seconds WHERE user_id = :user', {'seconds': seconds, 'user': user_id})
                await conn.commit()
                return True

    async def del_time(self, user_id: int, seconds: int):
        async with aiosqlite.connect(self.connector) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('UPDATE tempo_semanal SET tempo_total = tempo_total - :seconds WHERE user_id = :user', {'seconds': seconds, 'user': user_id})
                await conn.commit()
                return True

    async def reset_all_times(self):
        async with aiosqlite.connect(self.connector) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('UPDATE tempo_semanal SET tempo_total = 0')
                await conn.commit()
