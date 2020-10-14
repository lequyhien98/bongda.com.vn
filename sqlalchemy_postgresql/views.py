import os
from pprint import pprint

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cdn_token import token_cdn
from sqlalchemy_postgresql.config import DATABASE_URI
from sqlalchemy_postgresql.model import Base, Category, Article
from token_genertion import token
from PIL import Image

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


def create_article(title, excerpt, url, image_paths, og_image_path, og_image_url, desc, published_at, category_name):
    article = session.query(Article).filter(Article.url == url).first()
    if article:
        print('Cào rồi!')
        return
    category_id = session.query(Category).filter(Category.title == category_name).first().id
    article = Article(
        title=title,
        excerpt=excerpt,
        url=url,
        image_paths=image_paths,
        og_image_path=og_image_path,
        og_image_url=og_image_url,
        html=desc,
        published_at=published_at,
        category_id=category_id
    )
    session.add(article)
    session.commit()
    print('OK!')
    session.close_all()


def uploading_image(_og_image_path):
    url = "https://cdn1.codeprime.net/api/upload/"
    headers = {'Authorization': 'JWT {}'.format(token_cdn),
               'Content-Type': 'application/json'}

    files = {
        'file': open(_og_image_path, 'rb'),
        'namespace': 'bdx',
        'keep_original_name': 'yes',
        'also_verify': 'yes'
    }
    response = requests.request("POST", url, headers=headers, files=files).json()
    pprint(response)


def create_article_in_web(title, excerpt, category_name, desc, og_image):
    # Make an authenticated request to create a post
    headers = {'Authorization': 'Ghost {}'.format(token.decode())}
    url = 'https://www.bongdaxanh.com/ghost/api/v3/admin/posts/?source=html'
    body = {'posts': [{'title': title,
                       'custom_excerpt': excerpt,
                       'excerpt': excerpt,
                       'html': desc,
                       'tags': [category_name],
                       }]}
    r = requests.post(url, json=body, headers=headers)
    print(r)


def recreate_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
