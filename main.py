import datetime
import os
import urllib.error

import cloudscraper
import wget
from bs4 import BeautifulSoup
from content_processor import bytes_to_str, clean_up_html
from sqlalchemy_postgresql.views import create_league, recreate_tables, create_article, create_tables
from requests.exceptions import ConnectionError

dicSlug = {
    'bong-da-anh': 'Bóng Đá Anh',
    'bong-da-tbn': 'Bóng Đá Tây Ban Nha',
    'bong-da-y': 'Bóng Đá Ý',
    'bong-da-duc': 'Bóng Đá Đức',
    'bong-da-phap': 'Bóng Đá Pháp',
    'champions-league': 'Champions_League',
    'europa-league': 'Europa League',
    'tin-chuyen-nhuong': 'Tin Chuyển Nhượng',
    'viet-nam': 'Bóng Đá Việt Nam',
    'bong-da-chau-a': 'Bóng Đá Châu Á',
    'bong-da-chau-au': ' Bóng Đá Châu Âu',
    'bong-da-chau-my': 'Bóng Đá Châu Mỹ',
    'bong-da-chau-phi': 'Bóng Đá Châu Phi',
    'giao-huu': 'Giao Hữu'
}


def get_soup(_url):
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'linux',
            'mobile': False
        }
    )
    r = scraper.get(_url).content
    _soup = BeautifulSoup(r, 'html5lib')
    return _soup


def get_slug_list():
    return ['bong-da-anh', 'bong-da-tbn', 'bong-da-y', 'bong-da-duc', 'bong-da-phap', 'champions-league',
            'europa-league', 'tin-chuyen-nhuong', 'bong-da-chau-a', 'bong-da-chau-au', 'bong-da-chau-my',
            'bong-da-chau-phi', 'giao-huu']


def get_page_url(page, _slug_item):
    return 'http://www.bongda.com.vn/%s/p%s' % (_slug_item, page)


def create_directory(_title, _league_name):
    current_directory = os.getcwd()
    image_file = os.path.join(current_directory, 'Hình Ảnh')
    if not os.path.exists(image_file):
        os.makedirs(image_file)
    category_file = os.path.join(image_file, _league_name)
    if not os.path.exists(category_file):
        os.makedirs(category_file)
    final_directory = os.path.join(category_file, _title)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    return final_directory


def get_title(_soup):
    _title_tag = _soup.find('h1', {'class': 'time_detail_news'})
    if _title_tag is not None:
        for attribute in ["class", "id", "name", "style"]:
            del _title_tag[attribute]
    return _title_tag


def get_excerpt(_soup):
    excerpt_tag = _soup.find('p', {'class': 'sapo_detail fontbold'})
    if excerpt_tag:
        if excerpt_tag.span:
            excerpt_tag.span.decompose()
    for attribute in ["class", "id", "name", "style"]:
        del excerpt_tag[attribute]
    excerpt_tag = excerpt_tag.prettify()
    excerpt_tag = bytes_to_str(clean_up_html(excerpt_tag))
    return excerpt_tag


def get_image(_title, _desc_tag, _league_name):
    image_paths = []
    image_tags = _desc_tag.findAll('img')
    final_directory = create_directory(_title, _league_name)
    if image_tags:
        for index, image_tag in enumerate(image_tags, 1):
            image_url = image_tag['src']
            if not os.path.exists(final_directory):
                continue
            new_path = final_directory + '/%d.jpg' % index
            if not os.path.exists(new_path):
                file_name = wget.download(image_url, out=final_directory)
                os.rename(file_name, new_path)
                image_tag['alt'] = 'Hình %d' % index
            image_paths.append(new_path)
    return image_paths


def get_desc(_soup, _title_tag, _desc_tag):
    final_desc = ""
    for attribute in ["class", "id", "name", "style"]:
        del _title_tag[attribute]
    _title_tag = _title_tag.prettify()
    _title_tag = bytes_to_str(clean_up_html(_title_tag))
    final_desc += _title_tag
    _excerpt = get_excerpt(_soup)
    if _excerpt:
        final_desc += _excerpt

    '''Xóa 'Tiểu Lam | 22:21 06/10/2020' ở cuối trang'''
    date_tag = _desc_tag.find('div', {'class': 'text-right f13'})
    if date_tag:
        date_tag.extract()

    '''Xóa chú thích của clip vì nó là thẻ p nên xử lý ở đây'''
    for x in _desc_tag.find_all('div', {'class': 'dugout-video'}):
        if x == _desc_tag.findAll(True)[0]:
            p_tag = x.next_sibling.next_sibling
            p_tag.extract()
        else:
            p_tag = x.previous_sibling.previous_sibling
            p_tag.extract()

    '''Xóa những bài viết đề xuất có trong nội dung'''
    for i_tag in _desc_tag.findAll('li'):
        i_tag.decompose()

    '''Đổi thẻ figcaption thành div'''
    for figcaption in _desc_tag.findAll('figcaption'):
        figcaption.name = 'div'

    for tag in _desc_tag.findAll(True):
        for attribute in ["class", "id", "name", "style"]:
            del tag[attribute]
    del _desc_tag['class']

    _desc_tag = _desc_tag.prettify()
    _desc_tag = bytes_to_str(clean_up_html(_desc_tag))
    final_desc += _desc_tag
    final_desc = final_desc.translate(str.maketrans({"'": "''"}))
    return final_desc


def get_published_time(desc_tag):
    published_time_tag = desc_tag.findAll(True)[-1]
    published_time = published_time_tag.text.split('|')[-1].strip()
    published_time = datetime.datetime.strptime(published_time, "%H:%M %d/%m/%Y")
    return published_time


def handle_crawling(_url, _league_name):
    print(_url)
    try:
        _soup = get_soup(_url)
        title_tag = get_title(_soup)
        if title_tag:
            desc_tag = _soup.find('div', {'class': 'exp_content news_details'})

            title = title_tag.text.translate(str.maketrans({"'": "''"})).strip()
            published = get_published_time(desc_tag)
            image_paths = get_image(title, desc_tag, _league_name)
            desc = get_desc(_soup, title_tag, desc_tag)
            create_article(title, _url, image_paths, desc, published, _league_name)
    except urllib.error.URLError:
        return
    except ConnectionError:
        print('No response')
        return


if __name__ == '__main__':
    print('x')
    recreate_tables()
    print('x')
    slug_list = get_slug_list()
    for slug_item in slug_list:
        league_name = dicSlug[slug_item]
        create_league(league_name)
        for i in range(1, 2):
            url = get_page_url(i, slug_item)
            print(url)
            try:
                soup = get_soup(url)
            except ConnectionError:
                print('No response!')
                continue
            '''Tin mới nhất'''
            url_tag = soup.find('div', {'class': 'col630 fr'})
            if url_tag:
                url = url_tag.a['href']
                handle_crawling(url, league_name)
            '''List url của trang'''
            url_list = soup.find('ul', {'class': 'list_top_news list_news_cate'})
            for url_tag in url_list.findAll('li'):
                url = url_tag.a['href']
                handle_crawling(url, league_name)
