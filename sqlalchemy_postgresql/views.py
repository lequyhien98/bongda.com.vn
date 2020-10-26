from datetime import tzinfo, timedelta

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from token_genertion.cdn_token_genertion import cdn_token
from sqlalchemy_postgresql.config import DATABASE_URI
from sqlalchemy_postgresql.model import Base, Article, Source
from token_genertion.ghost_token_genertion import create_token, key
from slugify import slugify

engine = create_engine(DATABASE_URI)

# create a configured "Session" class
Session = sessionmaker(bind=engine, expire_on_commit=False)

# create a Session
session = Session()


def create_tables():
    Base.metadata.create_all(engine)


def recreate_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    create_source()


def create_source():
    session.add_all([
        Source(name='bongda.com.vn', url='http://www.bongda.com.vn/'),
        Source(name='bongdaplus.vn', url='https://bongdaplus.vn/')]
    )
    session.commit()
    session.close()


class VN(tzinfo):
    """A time zone with an arbitrary, constant +7:00 offset."""

    def utcoffset(self, dt):
        return timedelta(hours=7, minutes=00)


def get_source(_source_name):
    _source = session.query(Source).filter(Source.name == _source_name).first()
    if not _source:
        print('Nguồn này không tồn tại!')
        return None
    return _source


def get_slug(_title):
    _slug = slugify(_title)
    return _slug


def check_news(url, tag):
    news = session.query(Article).filter(Article.src_url == url).first()
    if news:
        slug = get_slug(news.title)
        is_published, news_id, updated_at, tags = get_post_by_slug(slug)
        if tag not in news.tags:
            news.tags = [*news.tags, tag]
            session.add(news)
            session.commit()
            if is_published:
                news.tags.append(tag)
                updating_a_post(news_id, news.tags, updated_at)
                print('Đã có trên Bongdaxanh.com!')
        print('Bài này có trong database!')
        return True
    else:
        return False


def create_article(title, url, bdx_url, tags, published_at, og_image_url, og_image_path, image_urls, image_paths,
                   excerpt, html, source):
    article = Article(
        title=title,
        src_url=url,
        bdx_url=bdx_url,
        tags=tags,
        published_at=published_at,
        og_image_url=og_image_url,
        og_image_path=og_image_path,
        image_urls=image_urls,
        image_paths=image_paths,
        excerpt=excerpt,
        html=html,
        source_id=source.id
    )
    session.add(article)
    session.commit()
    print('Lưu bài post vào database thành công!')
    session.close()


def uploading_og_image(_og_image_path):
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
        verify_upload(response.json()['verifyCode'])
    else:
        print('Uploading image is not successful')
    return _og_image_url


def uploading_image(image_path):
    _image_url = None
    url = "https://cdn1.codeprime.net/api/upload/"
    payload = {
        'namespace': 'bdx',
        'keep_original_name': 'yes',
        'resize_contain': '[\'740x400\']'
    }
    files = [
        ('file', open(image_path, 'rb'))
    ]
    response = requests.request("POST", url, data=payload, files=files)
    if response.ok:
        _image_url = response.json()['resizeContain']['740x400']['url']
        print('Uploading image is successful')
        verify_upload(response.json()['verifyCode'])
    else:
        print('Uploading image is not successful')
    return _image_url


def verify_upload(verify_code):
    url = "https://cdn1.codeprime.net/api/verify/"
    headers = {'Authorization': 'JWT {}'.format(cdn_token)}
    payload = {
        'verify_code': verify_code,
    }
    response = requests.post(url, data=payload, headers=headers)
    if response.ok:
        print('Verifying is successful')
    else:
        print('Verifying is not successful')


def create_article_in_web(title, tags, published_at, og_image_url, excerpt, html):
    # Make an authenticated request to create a post
    _id = None
    bdx_url = None
    ghost_token = create_token()
    headers = {'Authorization': 'Ghost {}'.format(ghost_token.decode())}
    url = 'https://www.bongdaxanh.com/ghost/api/v3/admin/posts/?source=html'
    body = {'posts': [{'title': title,
                       'status': 'published',
                       'html': html,
                       'feature_image': og_image_url,
                       'custom_excerpt': excerpt,
                       'excerpt': excerpt,
                       'og_image': og_image_url,
                       'og_title': title,
                       'og_description': excerpt,
                       'twitter_image': og_image_url,
                       'twitter_title': title,
                       'twitter_description': excerpt,
                       "meta_title": title,
                       "meta_description": excerpt,
                       'tags': tags,
                       'published_at': published_at,
                       'authors': [{
                           'name': 'Maintainer',
                           'slug': 'maintainer'
                       }],
                       }]}
    response = requests.post(url, json=body, headers=headers)
    print(response.text)
    if response.ok:
        for ele in response.json()['posts']:
            if ele['url']:
                bdx_url = ele['url']
                break
    return bdx_url


def get_post_by_slug(slug):
    news_id = None
    updated_at = None
    tags = []
    url = 'https://www.bongdaxanh.com/ghost/api/v3/content/posts/slug/%s/?key=%s&include=tags' % (slug, key)
    response = requests.get(url)
    if response.ok:
        news_id = response.json()['posts'][0]['id']
        updated_at = response.json()['posts'][0]['updated_at']
        json_tags = response.json()['posts'][0]['tags']
        for json_tag in json_tags:
            tags.append(json_tag['name'])
    return response.ok, news_id, updated_at, tags


def updating_a_post(news_id, tags, updated_at):
    url = 'https://www.bongdaxanh.com/ghost/api/v3/admin/posts/%s/?key=6639515e8b14a6b71a3e483479' % news_id
    ghost_token = create_token()
    headers = {'Authorization': 'Ghost {}'.format(ghost_token.decode())}
    body = {
        'posts': [{'tags': tags,
                   'updated_at': updated_at,
                   }]
    }
    response = requests.put(url, json=body, headers=headers)
    print(response)
