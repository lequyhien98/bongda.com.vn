from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return "<Category(title='{}')>".format(self.name)


class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True)
    published_at = Column(DateTime)
    og_image_url = Column(String)
    og_image_path = Column(String)
    image_urls = Column(ARRAY(String))
    image_paths = Column(ARRAY(String))
    excerpt = Column(String)
    html = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete='SET NULL'))

    def __repr__(self):
        return "<Article(title='{}', url='{}' published={})>" \
            .format(self.title, self.url, self.published_at)
