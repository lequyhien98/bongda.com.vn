import re
from lxml.html.clean import Cleaner


class NewCleaner(Cleaner):
    pass


cleaner = NewCleaner(
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
    allow_tags=['p', 'div', 'li', 'img', 'h1', 'figcaption', 'figure', 'em', 'strong', 'br', 'span'],
)


def clean_up_html(html):
    # Xóa class
    html = re.sub('class=".*?"', '', html)
    final_text = cleaner.clean_html(html)
    return final_text
