from datetime import tzinfo, timedelta, time
import requests
from django.utils.text import slugify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_postgresql.config import DATABASE_URI
from sqlalchemy_postgresql.model import Base, Article, Source
from token_genertion.cdn_token_genertion import cdn_token
from token_genertion.ghost_token_genertion import create_token, key
import time
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
        Source(name='bongda.com.vn', url='http://www.bongda.com.vn'),
        Source(name='bongdaplus.vn', url='https://bongdaplus.vn'),
        Source(name='24h.com.vn', url='https://www.24h.com.vn'),
        Source(name='thethao247.vn', url='https://thethao247.vn'),
        Source(name='vnexpress.net', url='https://vnexpress.net')
    ])
    session.commit()
    session.close()


class VN(tzinfo):
    """A time zone with an arbitrary, constant +7:00 offset."""

    def utcoffset(self, dt):
        return timedelta(hours=7, minutes=00)


def get_source(source_name):
    source = session.query(Source).filter(Source.name == source_name).first()
    if not source:
        print('Nguồn này không tồn tại!')
        return None
    return source


def get_slug(title):
    slug = slugify(title)
    return slug


def check_news(url, new_tag):
    news = session.query(Article).filter(Article.src_url == url).first()
    if news:
        is_published, updated_at, tags = get_post_by_id(news.news_id)
        if new_tag not in news.tags:
            news.tags = [*news.tags, new_tag]
            session.add(news)
            session.commit()
            if is_published:
                tags.append(new_tag)
                updating_a_post(news.news_id, tags, updated_at)
                print('Update tag trên Bongdaxanh.com!')
        print('Bài này có trong database!')
        return True
    else:
        return False


def check_bdx_news(title, new_tag, is_out):
    slug = get_slug(title)
    is_published, news_id, updated_at, tags = get_post_by_slug(slug)
    if news_id:
        if new_tag not in tags:
            if is_published:
                tags.append(new_tag)
                updating_a_post(news_id, tags, updated_at)
                print('Update tag trên Bongdaxanh.com!')
        else:
            is_out = True
        print('Bài này có trên Bongdaxanh.com!')
        return True, is_out
    else:
        return False, is_out


def create_article(title, slug, news_id, url, bdx_url, tags, published_at, og_image_url, og_image_path, image_urls,
                   image_paths,
                   excerpt, html, source):
    article = Article(
        title=title,
        slug=slug,
        news_id=news_id,
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


def uploading_og_image(og_image_path):
    og_image_url = None
    url = "https://cdn1.codeprime.net/api/upload/"
    payload = {
        'namespace': 'bdx',
        'keep_original_name': 'yes',
    }
    files = [
        ('file', open(og_image_path, 'rb'))
    ]
    response = requests.request("POST", url, data=payload, files=files)
    if response.ok:
        og_image_url = response.json()['original']['url']
        print('Uploading image is successful')
        verify_upload(response.json()['verifyCode'])
    else:
        print('Uploading image is not successful')
    return og_image_url


def uploading_image(image_path, width, height):
    image_url = None
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
        if width > 740 or height > 400:
            image_url = response.json()['original']['url']
        else:
            image_url = response.json()['resizeContain']['740x400']['url']
        print('Uploading image is successful')
        verify_upload(response.json()['verifyCode'])
    else:
        print('Uploading image is not successful')
    return image_url


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


def create_article_in_web(title, slug, tags, published_at, og_image_url, excerpt, html):
    # Make an authenticated request to create a post
    news_id = None
    bdx_url = None
    ghost_token = create_token()
    headers = {'Authorization': 'Ghost {}'.format(ghost_token.decode())}
    url = 'https://www.bongdaxanh.com/ghost/api/v3/admin/posts/?source=html'
    body = {'posts': [{'title': title,
                       'slug': slug,
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
            if ele['id']:
                news_id = ele['id']
            if ele['url']:
                bdx_url = ele['url']
                break
    return bdx_url, news_id


def get_post_by_id(news_id):
    updated_at = None
    tags = []
    url = 'https://www.bongdaxanh.com/ghost/api/v3/content/posts/%s/?key=%s&include=tags' % (news_id, key)
    response = requests.get(url)
    if response.ok:
        updated_at = response.json()['posts'][0]['updated_at']
        json_tags = response.json()['posts'][0]['tags']
        for json_tag in json_tags:
            tags.append(json_tag['name'])
    elif response.status_code == 429:
        time.sleep(int(response.headers["Retry-After"]))
    return response.ok, updated_at, tags


def get_post_by_slug(slug):
    news_id = None
    updated_at = None
    tags = []
    url = 'https://www.bongdaxanh.com/ghost/api/v3/content/posts/slug/%s/?key=%s&include=tags' % (slug, key)
    response = requests.get(url)
    print(response)
    if response.ok:
        news_id = response.json()['posts'][0]['id']
        updated_at = response.json()['posts'][0]['updated_at']
        json_tags = response.json()['posts'][0]['tags']
        for json_tag in json_tags:
            tags.append(json_tag['name'])
    elif response.status_code == 429:
        time.sleep(int(response.headers["Retry-After"]))
    return response.ok, news_id, updated_at, tags


def updating_a_post(news_id, tags, updated_at):
    url = 'https://www.bongdaxanh.com/ghost/api/v3/admin/posts/%s/?key=%s' % (news_id, key)
    ghost_token = create_token()
    headers = {'Authorization': 'Ghost {}'.format(ghost_token.decode())}
    body = {
        'posts': [{'tags': tags,
                   'updated_at': updated_at,
                   }]
    }
    response = requests.put(url, json=body, headers=headers)
    print(response.text)
