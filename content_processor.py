import re
from urllib.parse import urlsplit
from lxml.html.clean import Cleaner


class NewCleaner(Cleaner):
    def allow_embedded_url(self, el, _url):
        if self.whitelist_tags is not None and el.tag not in self.whitelist_tags:
            return False
        scheme, netloc, path, query, fragment = urlsplit(_url)
        netloc = netloc.lower().split(':', 1)[0]
        if scheme not in ('http', 'https', ''):
            return False
        if netloc in self.host_whitelist:
            return True
        return False


cleaner = NewCleaner(
    page_structure=True,
    meta=True,
    embedded=True,
    links=True,
    style=True,
    processing_instructions=True,
    inline_style=True,
    scripts=True,
    javascript=True,
    comments=True,
    frames=True,
    forms=True,
    annoying_tags=True,
    safe_attrs_only=True,
    remove_tags=('html', 'head', 'body', 'a', 'script'),
    allow_tags=['strong', 'i', 'b', 'em', 'p', 'div', 'li', 'img', 'h1', 'figcaption', 'figure'],
)


def bytes_to_str(bytes_text):
    try:
        return bytes_text.decode("utf-8")
    except AttributeError:
        return str(bytes_text)


def clean_up_html(html):
    html = re.sub('class=".*?"', '', html)
    final_text = cleaner.clean_html(html)
    return final_text
