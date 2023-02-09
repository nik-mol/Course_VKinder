import sqlalchemy
from sqlalchemy.orm import sessionmaker

from .db_models import create_tables, User, Favorite, Photo, BlackList
import configparser


def connect_to_db():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    user = config['DB']['user']
    password = config['DB']['password']
    DSN = f'postgresql://{user}:{password}@localhost:5432/vkinder_db'
    engine = sqlalchemy.create_engine(DSN)
    create_tables(engine)
    return engine


def add_user_to_db(user_id: int, name: str, surname: str, gender: int) -> bool:
    session = Session()
    try:
        user = User(user_id=user_id, name=name, surname=surname, gender=gender)
        session.add(user)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        session.close()


def add_favorite_to_db(user_id: int, favorite_for_id: int, name: str, surname: str) -> bool:
    session = Session()
    try:
        user = Favorite(user_id=user_id, favorite_for_id=favorite_for_id, name=name, surname=surname)
        session.add(user)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        session.close()


def add_photo_to_db(photo_list: list, favorite_id: int) -> bool:
    session = Session()
    try:
        photos = [Photo(photo_id=x, favorite_id=favorite_id) for x in photo_list]
        session.add_all(photos)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        session.close()


def get_favorites(user_id):
    session = Session()
    try:
        users = [[user.user_id, user.name, user.surname] for user in session.query(Favorite).all() if
                 user.favorite_for_id == user_id]
        return users
    except Exception as e:
        print(e)
        return False
    finally:
        session.close()


def add_user_to_blacklist(user_id, blocked_for_id):
    session = Session()
    try:
        user = BlackList(user_id=user_id, blocked_for_id=blocked_for_id)
        session.add(user)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        session.close()


def get_blacklist(user_id):
    session = Session()
    try:
        users = [user.user_id for user in session.query(BlackList).all() if user.blocked_for_id == user_id]
        return users
    except Exception as e:
        print(e)
        return False
    finally:
        session.close()


engine = connect_to_db()
Session = sessionmaker(bind=engine)
