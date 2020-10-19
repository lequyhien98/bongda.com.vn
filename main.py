import datetime
import os
import urllib.error
import cloudscraper
import wget
from bs4 import BeautifulSoup
from sqlalchemy_postgresql.views import recreate_tables, create_article, create_article_in_web, uploading_image, check_article, create_category
from requests.exceptions import ConnectionError

from utils.content_processor import clean_up_html

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


def get_category_page_url(_page, _slug_item):
    # http://www.bongda.com.vn/bong-da-anh/p1
    return 'http://www.bongda.com.vn/%s/p%s' % (_slug_item, _page)


def create_directory(_title, _league_name, is_thumbnail_image_path=False):
    # _title = _title.replace("\"", "").strip()
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
    # Nếu là thumbnail thì tạo riêng 1 thư mục khác
    if is_thumbnail_image_path:
        final_directory = os.path.join(final_directory, 'Thumbnail')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
    return final_directory


def get_title(_soup):
    _title = None
    _title_tag = _soup.find('h1', {'class': 'time_detail_news'})
    if _title_tag:
        _title = _title_tag.get_text(strip=True)
    print('Tên bài báo: %s' % _title)
    return _title


def get_excerpt(_soup):
    _excerpt = None
    _excerpt_tag = _soup.find('p', {'class': 'sapo_detail fontbold'})
    if _excerpt_tag:
        if _excerpt_tag.span:
            # Bỏ dòng bongda.com.vn đầu dòng
            _excerpt_tag.span.decompose()
        _excerpt = _excerpt_tag.get_text(strip=True)
    return _excerpt


def get_images(_title, _desc_tag, _category_name):
    image_paths = []
    image_urls = []

    # Tạo thư mục lưu ảnh
    final_directory = create_directory(_title, _category_name)

    # Tạo slug đặt tên cho img
    _slug = '{}'.format('bong-da-xanh')

    image_tags = _desc_tag.findAll('img')
    if image_tags:
        for index, image_tag in enumerate(image_tags, 1):
            # Lấy src của ảnh
            image_url = image_tag['src']

            # Tên path đặt ảnh mà bạn mong muốn
            new_path = final_directory + '/%s-%d.jpg' % (_slug, index)

            # Tải ảnh về
            file_name = wget.download(image_url, out=final_directory)

            # Đổi tên lại theo path mà bạn đã đặt
            os.rename(file_name, new_path)

            # Upload ảnh lên cdn với path mới
            image_tag['src'] = uploading_image(new_path)

            # Lưu lại để bỏ vào batabase
            image_paths.append(new_path)
            image_urls.append(image_tag['src'])

    return image_paths, image_urls


def get_og_image(_soup, _title, _league_name):
    og_image_path = None
    new_og_image_url = None

    # Tạo thư mục lưu ảnh
    final_directory = create_directory(_title, _league_name, True)

    # Tạo slug đặt tên cho img
    _slug_image = '/{}'.format('bong-da-xanh-thumbnail')

    _og_image_tag = _soup.find('meta', {'property': 'og:image'})
    if _og_image_tag:
        # Lấy src của ảnh
        _og_image_url = _og_image_tag['content']

        # Tên path đặt ảnh mà bạn mong muốn
        new_og_image_path = final_directory + '{}.jpg'.format(_slug_image)

        # Tải ảnh về
        file_name = wget.download(_og_image_url, out=final_directory)

        # Đổi tên lại theo path mà bạn đã đặt
        os.rename(file_name, new_og_image_path)

        # Upload ảnh lên cdn với path mới
        new_og_image_url = uploading_image(new_og_image_path)

        # Lưu lại để bỏ vào batabase
        og_image_path = new_og_image_path

    return og_image_path, new_og_image_url


def get_desc(_desc_tag):
    final_desc = ""

    # Xóa 'Tiểu Lam | 22:21 06/10/2020' ở cuối trang
    date_tag = _desc_tag.find('div', {'class': 'text-right f13'})
    if date_tag:
        date_tag.extract()

    # Xóa chú thích của clip vì nó là thẻ p nên xử lý ở đây
    #  Ví dụ: Những khoảnh khắc ấn tượng của ....
    for x in _desc_tag.find_all('div', {'class': 'dugout-video'}):
        if x == _desc_tag.findAll(True)[0]:
            p_tag = x.next_sibling.next_sibling
            p_tag.extract()
        else:
            p_tag = x.previous_sibling.previous_sibling
            p_tag.extract()

    # Xóa những bài viết đề xuất có trong nội dung (thẻ i)
    # Ví dụ:
    #  * Lộ diện 'người không phổi' mới ở Chelsea
    #  * Cầu thủ Chelsea đó đang là số 1 thế giới, Declan Rice chẳng thể thay thế'
    for i_tag in _desc_tag.findAll('li'):
        i_tag.decompose()

    del _desc_tag['class']
    for tag in _desc_tag.findAll(True):

        # Xóa thẻ a
        if tag.a:
            while tag.a:
                tag.a.unwrap()
            tag.smooth()

        # Xử lý thẻ figure
        if tag.name == 'figure':
            if tag.text.strip() in final_desc:
                continue
            tag.h2.unwrap()
            figcaption_tag = clean_up_html(str(tag))
            final_desc += figcaption_tag

        elif tag.name == 'p':
            if tag.text.strip() in final_desc:
                continue
            p_tag = clean_up_html(str(tag))
            final_desc += p_tag
    return final_desc


def get_published_at(_soup):
    published_at = None

    published_at_tag = _soup.find('div', {'class': 'time_comment'})
    if published_at_tag:
        published_at_text = published_at_tag.span.text.strip()
        time_text = published_at_text.split(' ')[0]
        date_text = published_at_text.split(' ')[-1]
        published_at_text = '%s %s' % (time_text, date_text)
        published_at = datetime.datetime.strptime(published_at_text, "%H:%M %d/%m/%Y")
    return published_at


def handle_crawling(_url, _category_name):
    try:
        _soup = get_soup(_url)

        title = get_title(_soup)

        if title:
            excerpt = get_excerpt(_soup)

            desc_tag = _soup.find('div', {'class': 'exp_content news_details'})

            # Lấy hình trong post lưu đường dẫn vào url
            image_paths, image_urls = get_images(title, desc_tag, _category_name)

            # Lấy hình trong og_image trong post lưu đường dẫn vào url để SEO
            og_image_path, og_image_url = get_og_image(_soup, title, _category_name)

            # Lấy thời gian publish của bài post trên web
            published_at = get_published_at(_soup)

            # Lấy nội dung của bài post
            _html = get_desc(desc_tag)

            # Lưu bài vào database
            create_article(title, _url, published_at, og_image_url, og_image_path, image_urls, image_paths, excerpt,
                           _html, _category_name)

            # Đăng lên web
            create_article_in_web(title, og_image_url, excerpt, _html, _category_name)
    except urllib.error.URLError as e:
        print(e)
        return
    except ConnectionError:
        print('No response')
        return


if __name__ == '__main__':
    recreate_tables()
    # Lấy các mục có trong trang (slug)
    # Ví dụ: bong-da-anh, bong-da-tbn
    slug_list = get_slug_list()
    for slug_item in slug_list:
        # Đổi slug sang tên của mục đó
        # 'bong-da-anh': 'Bóng Đá Anh'
        category_name = dicSlug[slug_item]
        create_category(category_name)

        # Trang của mục và số trang mà bạn muốn
        pages = 6
        for page in range(1, pages):
            category_page_url = get_category_page_url(page, slug_item)
            try:
                soup = get_soup(category_page_url)
            except ConnectionError:
                print('No response!')
                continue

            # Lấy tin mới nhất
            url_tag = soup.find('div', {'class': 'col630 fr'})
            if url_tag:
                article_url = url_tag.a['href']
                # Check xem bài post này đã có trong database chưa bằng việc xét url của nó
                if check_article(article_url):
                    continue
                handle_crawling(article_url, category_name)
            # List url của trang
            url_list = soup.find('ul', {'class': 'list_top_news list_news_cate'})
            if url_list:
                for url_tag in url_list.findAll('li'):
                    article_url = url_tag.a['href']
                    # Check xem bài post này đã có trong database chưa bằng việc xét url của nó
                    if check_article(article_url):
                        continue
                    handle_crawling(article_url, category_name)
            exit()
