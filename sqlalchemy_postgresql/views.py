from datetime import datetime
import arrow as arrow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_postgresql.config import DATABASE_URI
from sqlalchemy_postgresql.model import Base, Category, Article

engine = create_engine(DATABASE_URI)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()


def create_tables():
    Base.metadata.create_all(engine)


def create_league(category_title):
    category = session.query(Category).filter(Category.title == category_title).first()
    if category:
        return
    # Create
    category = Category(title=category_title)
    session.add(category)
    session.commit()
    session.close_all()


def create_article(title, url, image_paths, thumbnail_image_path, desc, published, category_name):
    article = session.query(Article).filter(Article.url == url).first()
    if article:
        return
    category_id = session.query(Category).filter(Category.title == category_name).first().id
    article = Article(
        title=title,
        url=url,
        image_paths=image_paths,
        thumbnail_image_path=thumbnail_image_path,
        description=desc,
        published=published,
        category_id=category_id
    )
    session.add(article)
    session.commit()
    session.close_all()


def recreate_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
