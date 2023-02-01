import psycopg2
from psycopg2 import errors
from forms import RegistrationForm
from models import Pet
from config import DBCONFIG
from typing import Optional, List, Tuple, Any

class DBConnNotOpen(Exception):
    '''
    Custom Exception raised when performing a database transaction
    without an open connection to the database.
    '''
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class OwnerDoesNotExist(Exception):
    '''
    Custom Exception raised when adding a record to `pets' table with an
    owner who is not present in the `Owners' table.
    '''
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class DB:
    '''
    Main database and operations handler static class
    '''
    conn: Optional[Any] = None
    cur: Optional[Any] = None

    def __init__(self):
        pass
    
    @classmethod
    def get_connection(cls) -> Any:
        '''
        Connect to database and return the connection.
        If an active connection already exists, return that instead.
        '''
        if not cls.conn:
            cls.conn = psycopg2.connect(
                f'dbname={ DBCONFIG["NAME"] } \
                  user={ DBCONFIG["USER"] } \
                  password={ DBCONFIG["PASS"] }'
            )
            cls.cur = cls.conn.cursor()
        return cls.conn

    @classmethod
    def disconnect(cls) -> None:
        '''
        Disconnect, close and clear database session
        '''
        if cls.cur: cls.cur.close()
        if cls.conn: cls.conn.close()


    @classmethod
    def create_all(cls) -> None:
        '''
        Creates all the database tables used throughout the session
        '''
        if not cls.cur: raise DBConnNotOpen()
        cls.cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS owners (
                id SERIAL PRIMARY KEY,
                name VARCHAR(64)
            );
            CREATE TABLE IF NOT EXISTS pets (
                id SERIAL PRIMARY KEY,
                category VARCHAR(4),
                breed VARCHAR(32),
                price FLOAT,
                owner INT REFERENCES owners (id) ON DELETE CASCADE
            );
            '''
        )

    @classmethod
    def insert(cls, form: RegistrationForm) -> None:
        if not cls.cur: raise DBConnNotOpen()

        pet = Pet(0, form.category.data, form.breed.data,
                  float(form.price.data), form.owner.data)

        cls.cur.execute(
            'select id from owners where name = %s', (pet.get_owner(),)
        )

        owner = cls.cur.fetchone()
        if not owner: raise OwnerDoesNotExist()
        owner_id: int = owner[0]

        cls.cur.execute(
            'insert into pets (category, breed, price, owner) \
            values (%s, %s, %s, %s)',
            (pet.get_category(), pet.get_breed(), pet.get_price(), owner_id)
        )

    @classmethod
    def update(cls, id: int, form: RegistrationForm) -> None:
        if not cls.cur: return  # TODO: raise exception

        pet = Pet(id, form.category.data, form.breed.data,
                  float(form.price.data), form.owner.data)

        cls.cur.execute(
            'select id from owners where name = %s;', (pet.get_owner(),)
        )

        owner = cls.cur.fetchone()
        if not owner: raise OwnerDoesNotExist()
        owner_id: int = owner[0]

        cls.cur.execute(
            'update pets \
                set category = %s, \
                    breed = %s, \
                    price = %s, \
                    owner = %s \
                where id = %s;',
            (
                pet.get_category(), pet.get_breed(), pet.get_price(), owner_id,
                pet.get_id()
            )
        )

    @classmethod
    def delete(cls, id: int) -> None:
        if not cls.cur: raise DBConnNotOpen()
        cls.cur.execute('delete from pets where id = %s', (id,))

    @classmethod
    def get_pets(cls) -> Optional[List[Pet]]:
        if not cls.cur: raise DBConnNotOpen()
        cls.cur.execute(
            'select pets.id, category, breed, price, owners.name \
            from pets, owners where pets.owner = owners.id;'
        )
        rows: Optional[List[Tuple[int, str, str, float, str]]] = \
            cls.cur.fetchall()
        if not rows: return None
        return [ Pet(*row) for row in rows ]

    @classmethod
    def get_pet(cls, id: int) -> Optional[Pet]:
        if not cls.cur: raise DBConnNotOpen()
        cls.cur.execute(
            'select pets.id, category, breed, price, owners.name \
            from pets, owners where pets.owner = owners.id and \
            pets.id = %s;', id
        )
        row: Optional[Tuple[int, str, str, float, str]] = cls.cur.fetchone()
        return None if not row else Pet(*row)

    @classmethod
    def commit(cls) -> None:
        if not cls.conn: raise DBConnNotOpen()
        cls.conn.commit()