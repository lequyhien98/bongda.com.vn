import datetime
import os
import re
import urllib.error
import cloudscraper
import slug
import wget
from bs4 import BeautifulSoup
from slugify import slugify
from content_processor import bytes_to_str, clean_up_html
from sqlalchemy_postgresql.views import recreate_tables, create_article, create_tables, \
    create_article_in_web, uploading_image, check_article, create_category
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


def create_directory(_title, _league_name, is_thumbnail_image_path=False):
    _title = _title.replace("\"", "").strip()
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
    if is_thumbnail_image_path:
        final_directory = os.path.join(final_directory, 'Thumbnail')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
    return final_directory


def get_title(_soup):
    _title = None
    _title_tag = _soup.find('h1', {'class': 'time_detail_news'})
    if _title_tag:
        _title = _title_tag.text.strip()
        '''Để lưu vào data base không bị lỗi cứ pháp'''
        # _title = _title.replace("'", "\'").strip()
    print('Tên bài báo: %s' % _title)
    return _title


def get_excerpt(_soup):
    _excerpt = ''
    _excerpt_tag = _soup.find('p', {'class': 'sapo_detail fontbold'})
    if _excerpt_tag:
        if _excerpt_tag.span:
            _excerpt_tag.span.decompose()
        _excerpt = _excerpt_tag.text.strip()
    return _excerpt


def get_images(_title, _desc_tag, _category_name):
    images = []
    image_urls = []

    image_tags = _desc_tag.findAll('img')

    '''Tạo thư mục lưu ảnh'''
    final_directory = create_directory(_title, _category_name)

    '''Tạo slug đặt tên cho img'''
    _slug = '{}'.format('bong-da-xanh')
    if image_tags:
        for index, image_tag in enumerate(image_tags, 1):
            '''Lấy src của ảnh'''
            image_url = image_tag['src']

            '''Path đặt ảnh mà bạn mong muốn'''
            new_path = final_directory + '/%s-%d.jpg' % (_slug, index)

            '''Tải ảnh về'''
            file_name = wget.download(image_url, out=final_directory)

            '''Đổi tên lại theo path mà bạn đã đặt'''
            os.rename(file_name, new_path)

            '''Upload ảnh lên cdn với path mới và lưu lại để bỏ vào database'''
            image_tag['src'] = uploading_image(new_path)
            image_urls.append(image_tag['src'])

            '''Lưu lại để bỏ vào batabase'''
            images.append(new_path)
    return images, image_urls


def get_og_image(_soup, _title, _league_name):
    og_image_path = None
    new_og_image_url = None

    '''Tạo thư mục lưu ảnh'''
    final_directory = create_directory(_title, _league_name, True)

    '''Tạo slug đặt tên cho img'''
    _slug_image = '/{}'.format('bong-da-xanh-thumbnail')
    # print('Slug tên của image: %s' % _slug_image)

    _og_image_tag = _soup.find('meta', {'property': 'og:image'})
    if _og_image_tag:
        '''Lấy src của ảnh'''
        _og_image_url = _og_image_tag['content']

        '''Path đặt ảnh mà bạn mong muốn'''
        new_og_image_path = final_directory + '{}.jpg'.format(_slug_image)

        '''Tải ảnh về'''
        file_name = wget.download(_og_image_url, out=final_directory)

        '''Đổi tên lại theo path mà bạn đã đặt'''
        os.rename(file_name, new_og_image_path)

        '''Upload ảnh lên cdn với path mới và lưu lại để bỏ vào database'''
        new_og_image_url = uploading_image(new_og_image_path)

        '''Lưu lại để bỏ vào batabase'''
        og_image_path = new_og_image_path
    return og_image_path, new_og_image_url


def get_desc(_desc_tag):
    final_desc = ""

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

    del _desc_tag['class']
    for tag in _desc_tag.findAll(True):
        if tag.a:
            while tag.a:
                tag.a.unwrap()
            tag.smooth()
        if tag.name == 'figure':
            if tag.text.strip() in final_desc:
                continue
            tag.h2.unwrap()
            figcaption_tag = tag.prettify()
            figcaption_tag = bytes_to_str(clean_up_html(figcaption_tag))
            final_desc += figcaption_tag
        elif tag.name == 'p':
            if tag.text.strip() in final_desc:
                continue
            p_tag = tag.prettify()
            p_tag = bytes_to_str(clean_up_html(p_tag))
            final_desc += p_tag
    final_desc = final_desc
    return final_desc


def get_published_at(_soup):
    published_at = None
    published_at_tag = _soup.find('div', {'class': 'time_comment'})
    if published_at_tag:
        published_at_text = published_at_tag.span.text.strip()
        time = published_at_text.split(' ')[0]
        date = published_at_text.split(' ')[-1]
        published_at_text = '%s %s' % (time, date)
        published_at = datetime.datetime.strptime(published_at_text, "%H:%M %d/%m/%Y")
    return published_at


def handle_crawling(_url, _category_name):
    print(_url)
    try:
        _soup = get_soup(_url)
        title = get_title(_soup)
        if title:
            excerpt = get_excerpt(_soup)
            desc_tag = _soup.find('div', {'class': 'exp_content news_details'})
            '''Images in Post'''
            image_paths, image_urls = get_images(title, desc_tag, _category_name)
            '''thumbnail Image'''
            og_image_path, og_image_url = get_og_image(_soup, title, _category_name)

            published_at = get_published_at(_soup)

            html = get_desc(desc_tag)
            '''Lưu bài vào database'''
            create_article(title, _url, published_at, og_image_url, og_image_path, image_urls, image_paths, excerpt, html, _category_name)
            create_article_in_web(title, og_image_url, excerpt, html, _category_name)
    except urllib.error.URLError:
        return
    except ConnectionError:
        print('No response')
        return


if __name__ == '__main__':
    # recreate_tables()
    slug_list = get_slug_list()
    for slug_item in slug_list:
        category_name = dicSlug[slug_item]
        create_category(category_name)
        for i in range(1, 2):
            url = get_page_url(i, slug_item)
            try:
                soup = get_soup(url)
            except ConnectionError:
                print('No response!')
                continue
            '''Tin mới nhất'''
            url_tag = soup.find('div', {'class': 'col630 fr'})
            if url_tag:
                article_url = url_tag.a['href']
                '''Check xem bài post này đã có trong database chưa bằng việc xét url của nó'''
                if check_article(article_url):
                    continue
                handle_crawling(article_url, category_name)
    #         '''List url của trang'''
    #         url_list = soup.find('ul', {'class': 'list_top_news list_news_cate'})
    #         if url_list:
    #             for url_tag in url_list.findAll('li'):
    #                 url = url_tag.a['href']
    #                 handle_crawling(url, league_name)
