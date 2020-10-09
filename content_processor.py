import re
from urllib.parse import urlsplit
import lxml
from lxml.html.clean import Cleaner, autolink_html


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
    page_structure=False,
    links=False,
    style=False,
    safe_attrs_only=True,
    embedded=False,
    remove_tags=('html', 'head', 'body', 'a', 'script'),
    allow_tags=['strong', 'i', 'b', 'em', 'p', 'div', 'br', 'li', 'img', 'h1'],
    remove_unknown_tags=False
)

_link_regexes = [re.compile(
    r'(?P<body>https?://(?P<host>[a-z0-9._-]+)(?:/[/\-_.,'
    r'a-z0-9ốẽỷăãđýỵẻưỡầéừơẩủớỉặậờàệỗễồụểẫũạằẵỳấíỹửìôứởẹộùêếịèẳáắềĩọổâợữảúự%&?;=~:@#+]*)?(?:\([/\-_.,'
    r'a-z0-9ốẽỷăãđýỵẻưỡầéừơẩủớỉặậờàệỗễồụểẫũạằẵỳấíỹửìôứởẹộùêếịèẳáắềĩọổâợữảúự%&?;=~:@#+]*\))?)',
    re.I)]


def bytes_to_str(bytes_text):
    try:
        return bytes_text.decode("utf-8")
    except AttributeError:
        return str(bytes_text)


def clean_up_html(html, method='html'):
    html = autolink_html(html, link_regexes=_link_regexes)
    html = lxml.html.fromstring(cleaner.clean_html(html))
    return lxml.html.tostring(html, encoding='utf-8', method=method)
