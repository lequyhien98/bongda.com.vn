import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from token_genertion.cdn_token_genertion import token_cdn
from sqlalchemy_postgresql.config import DATABASE_URI
from sqlalchemy_postgresql.model import Base, Category, Article
from token_genertion.ghost_token_genertion import token

engine = create_engine(DATABASE_URI)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()


def create_tables():
    Base.metadata.create_all(engine)


def recreate_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def check_article(url):
    print(url)
    article = session.query(Article).filter(Article.url == url).first()
    if article:
        print('Bài này đã tồn tại!')
        return True
    else:
        return False


def create_category(category_name):
    category = session.query(Category).filter(Category.name == category_name).first()
    if category:
        return
    # Create category
    category = Category(name=category_name)
    session.add(category)
    session.commit()
    print('Lưu tag vào database thành công!')
    session.close()


def create_article(title, url, published_at, og_image_url, og_image_path, image_urls, image_paths, excerpt, html,
                   category_name):
    category_id = session.query(Category).filter(Category.name == category_name).first().id
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
    print('Lưu bài post vào database thành công!')
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
    response = requests.request("POST", url, data=payload, files=files)
    if response.ok:
        _og_image_url = response.json()['original']['url']
        print('Uploading image is successful')
        # verify_upload(response.json()['verifyCode'])
    else:
        print('Uploading image is not successful')
    return _og_image_url


def verify_upload(verify_code):
    url = "https://cdn1.codeprime.net/api/verify/"
    headers = {'Authorization': 'JWT {}'.format(token_cdn)}
    payload = {
        'verify_code': verify_code,
    }
    response = requests.post(url, data=payload, headers=headers)
    if response.ok:
        print('Verifying is successful')
    else:
        print('Verifying is not successful')


def create_article_in_web(title, _og_image_url, excerpt, html, category_name):
    # Make an authenticated request to create a post
    _id = None
    headers = {'Authorization': 'Ghost {}'.format(token.decode())}
    url = 'https://www.bongdaxanh.com/ghost/api/v3/admin/posts/?source=html'
    body = {'posts': [{'title': title,
                       'html': html.replace('&nbsp;', '').strip(),
                       'feature_image': _og_image_url,
                       'custom_excerpt': excerpt,
                       'excerpt': excerpt,
                       'og_image': _og_image_url,
                       'og_title': title,
                       'og_description': excerpt,
                       'twitter_image': _og_image_url,
                       'twitter_title': title,
                       'twitter_description': excerpt,
                       "meta_title": title,
                       "meta_description": excerpt,
                       'tags': [category_name],
                       }]}
    response = requests.post(url, json=body, headers=headers)
    print(response)

