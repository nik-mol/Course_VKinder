import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=20))
    surname = sq.Column(sq.String(length=40))
    gender = sq.Column(sq.Integer)

    def __str__(self):
        return f'{self.user_id}: {self.name} {self.surname}'


class Favorite(Base):
    __tablename__ = 'favorites'

    user_id = sq.Column(sq.Integer, primary_key=True)
    favorite_for_id = sq.Column(sq.Integer, sq.ForeignKey("users.user_id"))
    name = sq.Column(sq.String(length=20))
    surname = sq.Column(sq.String(length=40))

    favorite_for_user = relationship(User, backref='favorites')

    def __str__(self):
        return f'Favorite user: {self.user_id} for user {self.favorite_for_id}'


class Photo(Base):
    __tablename__ = 'photos'

    id = sq.Column(sq.Integer, primary_key=True)
    photo_id = sq.Column(sq.String(length=60))
    favorite_id = sq.Column(sq.Integer, sq.ForeignKey("favorites.user_id"))

    favorite_photo = relationship(Favorite, backref='photos')

    def __str__(self):
        return f"Photo {self.photo_id} is {self.favorite_id} user's photo"


class BlackList(Base):
    __tablename__ = 'blacklist'

    user_id = sq.Column(sq.Integer, primary_key=True)
    blocked_for_id = sq.Column(sq.Integer, sq.ForeignKey("users.user_id"))

    favorite_user = relationship(User, backref='blacklist')

    def __str__(self):
        return f'Blocked user: {self.user_id}'


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
