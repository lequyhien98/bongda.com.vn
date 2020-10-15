from pprint import pprint

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_postgresql.config import DATABASE_URI
from sqlalchemy_postgresql.model import Base, Category, Article
from token_genertion import token

engine = create_engine(DATABASE_URI)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()


def create_tables():
    Base.metadata.create_all(engine)


def create_category(category_title):
    category = session.query(Category).filter(Category.title == category_title).first()
    if category:
        return
    # Create
    category = Category(title=category_title)
    session.add(category)
    session.commit()
    session.close()


def check_article(url):
    print(url)
    article = session.query(Article).filter(Article.url == url, Article.removed == False).first()
    if article:
        print('Bài này đã tồn tại!')
        return True
    else:
        return False


def create_article(title, url, published_at, og_image_url, og_image_path, image_urls, image_paths, excerpt, html,
                   category_name):
    category_id = session.query(Category).filter(Category.title == category_name).first().id
    article = Article(
        title=title,
        url=url,
        published_at=published_at,
        og_image_url=og_image_url,
        og_image_path=og_image_path,
        image_urls=image_urls,
        image_paths=image_paths,
        excerpt=excerpt,
        html=html,
        category_id=category_id
    )
    session.add(article)
    session.commit()
    print('Lưu vào database thành công!')
    session.close()


def uploading_image(_og_image_path):
    _og_image_url = None
    url = "https://cdn1.codeprime.net/api/upload/"
    payload = {
        'namespace': 'bdx',
        'keep_original_name': 'yes',
    }
    files = [
        ('file', open(_og_image_path, 'rb'))
    ]
    headers = {
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.ok:
        _og_image_url = response.json()['original']['url']
    return _og_image_url


def create_article_in_web(title, _og_image_url, excerpt, html, category_name):
    # Make an authenticated request to create a post
    headers = {'Authorization': 'Ghost {}'.format(token.decode())}
    url = 'https://www.bongdaxanh.com/ghost/api/v3/admin/posts/?source=html'
    body = {'posts': [{'title': title,
                       'og_title': title,
                       'twitter_title': title,
                       'feature_image': _og_image_url,
                       'tags': [category_name],
                       'og_image': _og_image_url,
                       'twitter_image': _og_image_url,
                       'og_description': excerpt,
                       'twitter_description': excerpt,
                       'custom_excerpt': excerpt,
                       'excerpt': excerpt,
                       'html': html
                       }]}
    response = requests.post(url, json=body, headers=headers)
    print(response)


def recreate_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
