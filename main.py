import http.client
import re
import time
from datetime import datetime, tzinfo, timedelta, timezone
import os
import urllib.error
import cloudscraper
import wget
from bs4 import BeautifulSoup
from dateutil.parser import parse
from selenium import webdriver
from sqlalchemy_postgresql.views import recreate_tables, create_article, create_article_in_web, uploading_image, \
    create_tables, uploading_og_image, get_source, check_news, get_slug, get_post_by_id, updating_a_post, check_bdx_news
from requests.exceptions import ConnectionError
from utils.content_processor import clean_up_html
from PIL import Image


def get_slug_list():
    if source.name == 'bongda.com.vn':
        return ['bong-da-anh', 'ngoai-hang-anh', 'cup-lien-doan-anh', 'cup-fa', 'tin-khac-anh', 'bong-da-tbn',
                'la-liga', 'cup-nha-vua', 'bong-da-y', 'serie-a', 'cup-quoc-gia-y', 'tin-khac-italia', 'bong-da-duc',
                'bundesliga', 'cup-quoc-gia-duc', 'tin-khac-duc', 'bong-da-phap', 'ligue-1', 'cup-lien-doan-phap',
                'tin-khac-phap', 'champions-league', 'europa-league', 'tin-chuyen-nhuong', 'hau-truong-san-co',
                'viet-nam', 'doi-tuyen-quoc-gia', 'cup-quoc-gia-vn', 'hang-nhat-vn', 'giai-tre-vn', 'bong-da-nu', 'vff',
                'tin-khac-vn', 'bong-da-chau-a', 'sea-games', 'euro-2020', 'asian-cup', 'giao-huu', 'bong-da-chau-au',
                'bong-da-chau-my', 'bong-da-chau-phi']
    elif source.name == 'bongdaplus.vn':
        return ['ngoai-hang-anh', 'bong-da-tay-ban-nha', 'bong-da-y', 'bong-da-duc', 'bong-da-phap',
                'champions-league-cup-c1', 'europa-league', 'chuyen-nhuong', 'bong-da-viet-nam']
    elif source.name == '24h.com.vn':
        return ['bong-da-ngoai-hang-anh-c149', 'bong-da-duc-c152', 'bong-da-y-c150', 'bong-da-tay-ban-nha-c151',
                'bong-da-phap-c344', 'bong-da-viet-nam-c182', 'cup-c1-champions-league-c153', 'tin-chuyen-nhuong-c53',
                'europa-league-c48e4044']


def get_sub_slug_list():
    return ['v-league', 'hang-nhat', 'cup-quoc-gia', 'dtqg', 'bong-da-nu', 'u17-quoc-gia', 'aff-suzuki-cup',
            'afc-champions-league', 'afc-cup', 'cac-doi-tuyen-tre', 'futsal', 'tin-khac']


def get_slug_dict():
    if source.name == 'bongda.com.vn':
        return {
            'bong-da-anh': 'Bóng Đá Anh',
            'ngoai-hang-anh': 'Ngoại Hạng Anh',
            'cup-lien-doan-anh': 'Cúp Liên Đoàn Anh',
            'cup-fa': 'Cúp FA',
            'tin-khac-anh': 'Tin khác Anh',
            'la-liga': 'La Liga',
            'cup-nha-vua': 'Cúp Nhà Vua',
            'tin-khac-tbn': 'Tin Khác Tây Ban Nha',
            'bong-da-tbn': 'Bóng Đá Tây Ban Nha',
            'bong-da-y': 'Bóng Đá Ý',
            'serie-a': 'Seria',
            'cup-quoc-gia-y': 'Cúp Quốc Gia Ý',
            'tin-khac-italia': 'Tin Khác Ý',
            'bong-da-duc': 'Bóng Đá Đức',
            'bundesliga': 'Bundesliga',
            'cup-quoc-gia-duc': 'Cúp Quốc Gia Đức',
            'tin-khac-duc': 'Tin Khác Đức',
            'bong-da-phap': 'Bóng Đá Pháp',
            'ligue-1': 'Ligue 1',
            'cup-lien-doan-phap': 'Cúp Liên Đoàn Pháp',
            'tin-khac-phap': 'Tin Khác Pháp',
            'hau-truong-san-co': 'Hậu Trường',
            'champions-league': 'Champions League',
            'europa-league': 'Europa League',
            'tin-chuyen-nhuong': 'Tin Chuyển Nhượng',
            'viet-nam': 'Bóng Đá Việt Nam',
            'doi-tuyen-quoc-gia': 'Các Đội Tuyển Quốc Gia Việt Nam',
            'v-league': 'V-League',
            'cup-quoc-gia-vn': 'Cúp Quốc Gia Việt Nam',
            'hang-nhat-vn': 'Hạng Nhất Việt Nam',
            'giai-tre-vn': 'Giải Trẻ Việt Nam',
            'bong-da-nu': 'Bóng Đá Nữ Việt Nam',
            'vff': 'VFF',
            'tin-khac-vn': 'Tin Khác Bóng Đá Việt Nam',
            'bong-da-chau-a': 'Bóng Đá Châu Á',
            'sea-games': 'Sea Games',
            'euro-2020': 'Euro 2020',
            'asian-cup': 'Asian Cup',
            'giao-huu': 'Giao Hữu',
            'bong-da-chau-au': 'Bóng Đá Châu Âu',
            'bong-da-chau-my': 'Bóng Đá Châu Mỹ',
            'bong-da-chau-phi': 'Bóng Đá Châu Phi'
        }
    elif source.name == 'bongdaplus.vn':
        return {
            'ngoai-hang-anh': 'Bóng Đá Anh',
            'bong-da-tay-ban-nha': 'Bóng Đá Tây Ban Nha',
            'bong-da-y': 'Bóng Đá Ý',
            'bong-da-duc': 'Bóng Đá Đức',
            'bong-da-phap': 'Bóng Đá Pháp',
            'champions-league-cup-c1': 'Champions League',
            'europa-league': 'Europa League',
            'chuyen-nhuong': 'Tin Chuyển Nhượng',
            'bong-da-viet-nam': 'Bóng Đá Việt Nam'
        }
    elif source.name == '24h.com.vn':
        return {
            'bong-da-ngoai-hang-anh-c149': 'Bóng Đá Anh',
            'bong-da-tay-ban-nha-c151': 'Bóng Đá Tây Ban Nha',
            'bong-da-y-c150': 'Bóng Đá Ý',
            'bong-da-duc-c152': 'Bóng Đá Đức',
            'bong-da-phap-c344': 'Bóng Đá Pháp',
            'cup-c1-champions-league-c153': 'Champions League',
            'europa-league-c48e4044': 'Europa League',
            'tin-chuyen-nhuong-c53': 'Tin Chuyển Nhượng',
            'bong-da-viet-nam-c182': 'Bóng Đá Việt Nam'
        }


def get_sub_slug_dict():
    _sub_dicSlug = {
        'v-league': 'V-League',
        'hang-nhat': 'Hạng Nhất Việt Nam',
        'cup-quoc-gia': 'Cúp Quốc Gia Việt Nam',
        'dtqg': 'Đội Tuyển Quốc Gia Việt Nam',
        'bong-da-nu': 'Bóng Đá Nữ Việt Nam',
        'u17-quoc-gia': 'U17 Quốc Gia Việt Nam',
        'aff-suzuki-cup': 'AFF Suzuki Cup',
        'afc-champions-league': 'AFC Champions League',
        'afc-cup': 'AFC Cup',
        'cac-doi-tuyen-tre': 'Các Đội Tuyển Trẻ Việt Nam',
        'futsal': 'Bóng Đá Futsal Việt Nam',
        'tin-khac': 'Tin Khác Bóng Đá Việt Nam'
    }
    return _sub_dicSlug


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


def set_up():
    '''Sử dụng Selenium'''
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    _driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=options)
    return _driver


class VN(tzinfo):
    """A time zone with an arbitrary, constant +7:00 offset."""

    def utcoffset(self, dt):
        return timedelta(hours=7, minutes=00)


def get_tags(news_soup):
    tags = [category_name]
    a_tags = None
    if source.name == 'bongda.com.vn':
        list_tag_trend_tag = news_soup.find('div', {'class': 'list_tag_trend'})
        if list_tag_trend_tag:
            a_tags = list_tag_trend_tag.findAll('a')
    elif source.name == 'bongdaplus.vn':
        cattags_tag = news_soup.find('div', {'class': 'cattags'})
        if cattags_tag:
            a_tags = cattags_tag.find_all('a', {'class': 'hashtag'})
    elif source.name == '24h.com.vn':
        sbnws_tag = news_soup.find('div', {'class': 'sbNws'})
        if sbnws_tag:
            a_tags = sbnws_tag.findAll('a')
    if not a_tags:
        return tags
    for a_tag in a_tags:
        if 'Champions League' in a_tag.get_text(strip=True):
            a_tag.string.replace_with('Champions League')
        if 'La Liga' in a_tag.get_text(strip=True):
            a_tag.string.replace_with('La Liga')
        if 'Ligue 1' in a_tag.get_text(strip=True):
            a_tag.string.replace_with('Ligue 1')
        if 'V-League' in a_tag.get_text(strip=True):
            a_tag.string.replace_with('V-League')
        if 'Bundesliga' in a_tag.get_text(strip=True):
            a_tag.string.replace_with('Bundesliga')
        if 'Europa League' in a_tag.get_text(strip=True):
            a_tag.string.replace_with('Europa League')
        if 'Serie A' in a_tag.get_text(strip=True):
            a_tag.string.replace_with('Serie A')
        if 'Premier League' in a_tag.get_text(strip=True):
            a_tag.string.replace_with('Premier League')
            tags.append('Ngoại Hạng Anh')
        if 'HLV' in a_tag.get_text(strip=True):
            tag_name = a_tag.text.replace('HLV', '').strip()
            a_tag.string.replace_with(tag_name)
        if 'F.C' in a_tag.get_text(strip=True):
            tag_name = a_tag.text.replace('F.C', '').strip()
            a_tag.string.replace_with(tag_name)
        if len(a_tag.get_text(strip=True)) > 0:
            if not a_tag.get_text(strip=True) in tags:
                tags.append(a_tag.get_text(strip=True).title())
    if source.name == 'bongdaplus.vn':
        if slug_item == 'bong-da-viet-nam':
            tags.append(extra_category_name)
    return tags


def get_category_page_url(page):
    if source.name == 'bongda.com.vn':
        # http://www.bongda.com.vn/bong-da-anh/p1
        return 'http://www.bongda.com.vn/%s/p%s' % (slug_item, page)
    elif source.name == 'bongdaplus.vn':
        if slug_item == 'bong-da-viet-nam':
            return 'https://bongdaplus.vn/%s/' % slug_item
        return 'https://bongdaplus.vn/%s.html' % slug_item
    elif source.name == '24h.com.vn':
        return 'https://www.24h.com.vn/%s.html?vpage=%s' % (slug_item, page)


def create_directory(title, is_thumbnail_image_path=False):
    current_directory = os.getcwd()
    image_file = os.path.join(current_directory, 'Images')
    if not os.path.exists(image_file):
        os.makedirs(image_file)
    category_file = os.path.join(image_file, category_name)
    if not os.path.exists(category_file):
        os.makedirs(category_file)
    final_directory = os.path.join(category_file, title)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    # Nếu là thumbnail thì tạo riêng 1 thư mục khác
    if is_thumbnail_image_path:
        final_directory = os.path.join(final_directory, 'Thumbnail')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
    return final_directory


def get_title(news_soup):
    title = None
    title_tag = None
    if source.name == 'bongda.com.vn':
        title_tag = news_soup.find('h1', {'class': 'time_detail_news'})
    elif source.name == 'bongdaplus.vn':
        title_tag = news_soup.find('h1', {'class': 'artitle'})
    elif source.name == '24h.com.vn':
        title_tag = news_soup.find('h1', {'id': 'article_title'})
    if title_tag:
        title = title_tag.get_text(strip=True)
    print('Tên bài báo: %s' % title)
    return title


def get_excerpt(news_soup):
    excerpt = None
    excerpt_tag = None
    if source.name == 'bongda.com.vn':
        excerpt_tag = news_soup.find('p', {'class': 'sapo_detail fontbold'})
        if excerpt_tag:
            if excerpt_tag.span:
                # Bỏ dòng bongda.com.vn đầu dòng
                excerpt_tag.span.decompose()
    elif source.name == 'bongdaplus.vn':
        excerpt_tag = news_soup.find('div', {'class': 'summary'})
    elif source.name == '24h.com.vn':
        excerpt_tag = news_soup.find('h2', {'id': 'article_sapo'})
    if excerpt_tag:
        excerpt = excerpt_tag.get_text(strip=True)
    if len(excerpt) > 300:
        excerpt = ''
    return excerpt


def get_images(title, news_soup):
    image_paths = []
    image_urls = []
    image_tags = None
    # Tạo thư mục lưu ảnh
    final_directory = create_directory(title)

    # Tạo slug đặt tên cho img
    slug = '{}'.format('bong-da-xanh')
    if source.name == 'bongda.com.vn':
        desc_tag = news_soup.find('div', {'class': 'exp_content news_details'})
        image_tags = desc_tag.findAll('img')
    elif source.name == 'bongdaplus.vn':
        desc_tag = news_soup.find('div', {'id': 'postContent'})
        image_tags = desc_tag.findAll('img')
    elif source.name == '24h.com.vn':
        desc_tag = news_soup.find('section', {'class': 'enter-24h-cate-article'})
        image_tags = desc_tag.find_all('img', {'class': 'news-image'})
    if image_tags:
        for index, image_tag in enumerate(image_tags, 1):
            # Lấy src của ảnh
            image_url = image_tag['src']
            if 'https' not in image_url:
                image_url = image_tag['data-original']
            # Tên path đặt ảnh mà bạn mong muốn
            new_path = final_directory + '/%s-%d.jpg' % (slug, index)

            # Tải ảnh về
            file_name = wget.download(image_url, out=final_directory)

            # Đổi tên lại theo path mà bạn đã đặt
            os.rename(file_name, new_path)

            if os.stat(new_path).st_size < 1000:
                continue

            with Image.open(new_path) as img:
                width, height = img.size
            # Upload ảnh lên cdn với path mới
            image_tag['src'] = uploading_image(new_path, width, height)

            # Lưu lại để bỏ vào batabase
            image_paths.append(new_path)
            image_urls.append(image_tag['src'])

    return image_paths, image_urls


def get_og_image(title, news_soup):
    og_image_path = None
    new_og_image_url = None
    og_image_tag = None

    # Tạo thư mục lưu ảnh
    final_directory = create_directory(title, True)

    # Tạo slug đặt tên cho img
    slug = '/{}'.format('bong-da-xanh')
    if source.name == 'bongda.com.vn':
        og_image_tag = news_soup.find('meta', {'property': 'og:image'})
    elif source.name == 'bongdaplus.vn':
        og_image_tag = news_soup.find('meta', {'property': 'og:image'})
    elif source.name == '24h.com.vn':
        og_image_tag = news_soup.find('meta', {'property': 'og:image'})
    if og_image_tag:
        # Lấy src của ảnh
        og_image_url = og_image_tag['content']

        # Tên path đặt ảnh mà bạn mong muốn
        new_og_image_path = final_directory + '{}.jpg'.format(slug)

        # Tải ảnh về
        file_name = wget.download(og_image_url, out=final_directory)

        # Đổi tên lại theo path mà bạn đã đặt
        os.rename(file_name, new_og_image_path)

        # Upload ảnh lên cdn với path mới
        new_og_image_url = uploading_og_image(new_og_image_path)

        # Lưu lại để bỏ vào batabase
        og_image_path = new_og_image_path

    return og_image_path, new_og_image_url


def get_desc(news_soup):
    final_desc = ""
    if source.name == 'bongda.com.vn':
        desc_tag = news_soup.find('div', {'class': 'exp_content news_details'})

        # Xóa 'Tiểu Lam | 22:21 06/10/2020' ở cuối trang
        date_tag = desc_tag.find('div', {'class': 'text-right f13'})
        if date_tag:
            date_tag.extract()

        # Xóa chú thích của clip vì nó là thẻ p nên xử lý ở đây
        #  Ví dụ: Những khoảnh khắc ấn tượng của ....
        for tag in desc_tag.find_all('div', {'class': 'dugout-video'}):
            if tag == desc_tag.findAll(True)[0]:
                p_tag = tag.next_sibling.next_sibling
                p_tag.extract()
            else:
                p_tag = tag.previous_sibling.previous_sibling
                p_tag.extract()

        # Xóa những bài viết đề xuất có trong nội dung (thẻ i)
        # Ví dụ:
        #  * Lộ diện 'người không phổi' mới ở Chelsea
        #  * Cầu thủ Chelsea đó đang là số 1 thế giới, Declan Rice chẳng thể thay thế'
        for i_tag in desc_tag.findAll('li'):
            i_tag.decompose()

        del desc_tag['class']
        for tag in desc_tag.findAll(True):

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
                figure_tag = clean_up_html(str(tag))
                final_desc += figure_tag

            elif tag.name == 'p':
                if tag.text.strip() in final_desc:
                    continue
                p_tag = clean_up_html(str(tag))
                final_desc += p_tag
    elif source.name == 'bongdaplus.vn':
        desc_tag = news_soup.find('div', {'id': 'postContent'})
        is_delete = False
        for tag in desc_tag.findAll(True):
            if is_delete:
                continue
            if tag.name == 'figure':
                figure_tag = clean_up_html(str(tag))
                final_desc += figure_tag
            elif tag.name == 'p':
                if tag.text.strip() in final_desc:
                    if not tag.img:
                        continue
                    else:
                        tag.name = 'figure'
                        alt = tag.img.attrs['alt']
                        if alt:
                            new_figcaption_tag = news_soup.new_tag('figcaption')
                            new_figcaption_tag.string = alt
                            tag.append(new_figcaption_tag)
                if tag.strong:
                    if tag.get_text(strip=True) == 'XEM THÊM':
                        is_delete = True
                        continue
                p_tag = clean_up_html(str(tag))
                final_desc += p_tag
            elif tag.name == 'table':
                if tag.text.strip() in final_desc:
                    continue
                table_tag = clean_up_html(str(tag))
                final_desc += table_tag
    elif source.name == '24h.com.vn':
        article_tag = news_soup.find('article', {'id': 'article_body'})
        is_crawl = True
        for tag in article_tag.findAll(True):
            if is_crawl:
                if tag.name == 'p':
                    if tag.em or tag.name == 'em':
                        continue
                    if tag.attrs.get('class') == ['linkOrigin']:
                        is_crawl = False
                        continue
                    if tag.img:
                        if tag.attrs.get('align'):
                            tag.name = 'figure'
                            new_figcaption_tag = news_soup.new_tag('figcaption')
                            new_figcaption_tag.string = tag.next_sibling.next_sibling.get_text(strip=True)
                            tag.append(new_figcaption_tag)
                            final_desc += clean_up_html(str(tag))
                            continue
                        else:
                            continue
                    if tag.get_text(strip=True) in final_desc:
                        continue
                    final_desc += clean_up_html(str(tag))
    final_desc += '<p>Nguồn: %s</p>' % source.name
    return final_desc


def get_published_at(news_soup):
    year, month, day, hour, minute = None, None, None, None, None
    if source.name == 'bongda.com.vn':
        published_at_tag = news_soup.find('div', {'class': 'time_comment'})
        if published_at_tag:
            published_at_text = published_at_tag.span.text.strip()
            time_text = published_at_text.split(' ')[0]
            time_split = time_text.split(':')
            date_text = published_at_text.split(' ')[-1]
            date_slit = date_text.split('/')
            day = int(date_slit[0])
            month = int(date_slit[1])
            year = int(date_slit[2])
            hour = int(time_split[0])
            minute = int(time_split[1])
    elif source.name == 'bongdaplus.vn':
        published_at_tag = news_soup.find('div', {'class': 'dtepub'})
        if published_at_tag:
            published_at_text = published_at_tag.get_text(strip=True)
            date_text = published_at_text.split(' ')[3]
            date_slit = date_text.split('-')
            time_text = published_at_text.split(' ')[1]
            time_split = time_text.split(':')
            day = int(date_slit[0])
            month = int(date_slit[1])
            year = int(date_slit[2])
            hour = int(time_split[0])
            minute = int(time_split[1])
    elif source.name == '24h.com.vn':
        published_at_tag = news_soup.find('div', {'class': 'updTm updTmD mrT5'})
        if published_at_tag:
            published_at_text = published_at_tag.get_text(strip=True)
            date_text = published_at_text.split(' ')[-4]
            time_text = published_at_text.split(' ')[-3]
            date_text_split = date_text.split('/')
            year = int(date_text_split[2])
            month = int(date_text_split[1])
            day = int(date_text_split[0])
            time_text_split = time_text.split(':')
            hour = int(time_text_split[0])
            minute = int(time_text_split[1])
    published_at = datetime(year, month, day, hour, minute, tzinfo=VN()).isoformat()
    return published_at


def crawl_a_news(url_item):
    try:
        news_soup = get_soup(url_item)

        title = get_title(news_soup)
        if title:
            is_published, _is_out = check_bdx_news(title, category_name, False)
            if _is_out:
                return True
            if not is_published:
                # Lấy thời gian publish của bài post trên web
                published_at = get_published_at(news_soup)
                utc_dt = datetime.now(timezone.utc)  # UTC time
                now_date = utc_dt.astimezone().date()  # local time
                published_at_date = parse(published_at).date()
                if not (now_date - timedelta(days=0) == published_at_date):
                    print('Bài này cũ rồi!')
                    return True
                tags = get_tags(news_soup)

                excerpt = get_excerpt(news_soup)

                slug = get_slug(title)

                # Lấy hình trong post lưu đường dẫn vào url
                image_paths, image_urls = get_images(title, news_soup)

                # Lấy hình trong og_image trong post lưu đường dẫn vào url để SEO
                og_image_path, og_image_url = get_og_image(title, news_soup)

                # Lấy nội dung của bài post
                html = get_desc(news_soup)

                #     # Đăng lên web
                bdx_url, news_id = create_article_in_web(title, slug, tags, published_at, og_image_url, excerpt, html)

                #     # Lưu bài vào database
                create_article(title, slug, news_id, url_item, bdx_url, tags, published_at, og_image_url, og_image_path,
                               image_urls, image_paths, excerpt, html, source)
    except urllib.error.URLError as e:
        print(e)
        return
    except ConnectionError:
        print('No response')
        return
    except http.client.InvalidURL:
        print('Url của hình không hợp lệ')
        return
    except AttributeError:
        print("There is no such attribute")
        return
    except KeyError as name:
        print(name)
        return
    except TypeError as name:
        print(name)
        return


def get_url_list(category_page_soup):
    url_list = []
    if source.name == 'bongda.com.vn':
        # Lấy tin mới nhất
        news_url_tag = category_page_soup.find('div', {'class': 'col630 fr'})
        if news_url_tag:
            for a_tag in news_url_tag.findAll('a', href=re.compile('^http://www.bongda.com.vn/')):
                if a_tag.img:
                    news_url = a_tag.get('href')
                    # Check xem bài post này đã có trong database chưa bằng việc xét url của nó
                    if not check_news(news_url, category_name):
                        url_list.append(news_url)
    elif source.name == 'bongdaplus.vn':
        for tag in category_page_soup.findAll('a', href=re.compile('^/{}/'.format(slug_item))):
            news_url = '%s%s' % (source.url, tag.get('href'))
            if news_url in url_list:
                continue
            # Check xem bài post này đã có trong database chưa bằng việc xét url của nó
            if not check_news(news_url, category_name):
                url_list.append(news_url)
    elif source.name == '24h.com.vn':
        category_page_soup.find('div', {'class': 'hotnew'}).decompose()
        section_tag = category_page_soup.find('section', {'class': 'enter-24h-cate-page'})
        url_list = []
        for a_tag in section_tag.findAll('a', href=re.compile('^https://www.24h.com.vn/bong-da/')):
            if a_tag.get('href') in url_list:
                continue
            url_list.append(a_tag.get('href'))
            print(a_tag.get('href'))
    return url_list


def get_category_page_soup():
    page = 1
    category_page_soup = None
    if source.name in ['bongda.com.vn', '24h.com.vn']:
        for page in range(1, page + 1):
            category_page_url = get_category_page_url(page)
            try:
                category_page_soup = get_soup(category_page_url)
            except ConnectionError:
                print('No response!')
                continue
        return category_page_soup
    elif source.name == 'bongdaplus.vn':
        driver = set_up()
        category_page_url = get_category_page_url(0)
        if slug_item == 'bong-da-viet-nam':
            category_page_url = '%s%s.html' % (category_page_url, sub_slug)
        print(category_page_url)
        driver.get(category_page_url)
        if page != 1:
            for index in range(1, page):
                more_button_tag = driver.find_element_by_class_name('addmore')
                if more_button_tag:
                    more_button_tag.click()
                time.sleep(2)
        html = driver.page_source
        category_page_soup = BeautifulSoup(html, 'html5lib')
        return category_page_soup


def crawl():
    url_list = []
    category_page_soup = get_category_page_soup()
    if category_page_soup:
        url_list = get_url_list(category_page_soup)
    if not url_list:
        return
    for url_item in url_list:
        print(url_item)
        if crawl_a_news(url_item):
            return True
        time.sleep(1)
    exit()
    return False


if __name__ == '__main__':
    sub_slug = None
    is_out = False
    recreate_tables()
    print('Nhập tên nguồn muốn cào:')
    print('Ví dụ: bongda.com.vn, bongdaplus.vn, 24h.com.vn')
    source_name = '24h.com.vn'
    source = get_source(source_name)
    if source:
        # Lấy các mục có trong trang (slug)
        # Ví dụ: bong-da-anh, bong-da-tbn
        slug_list = get_slug_list()
        for slug_item in slug_list:
            # Đổi slug sang tên của mục đó
            # 'bong-da-anh': 'Bóng Đá Anh'
            slugDic = get_slug_dict()
            category_name = slugDic[slug_item]
            if source.name == 'bongdaplus.vn' and slug_item == 'bong-da-viet-nam':
                sub_slug_list = get_sub_slug_list()
                for sub_slug in sub_slug_list:
                    sub_slugDic = get_sub_slug_dict()
                    extra_category_name = sub_slugDic[sub_slug]
                    if crawl():
                        continue
            else:
                if crawl():
                    continue
