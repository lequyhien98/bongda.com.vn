from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    order = Column(Integer, default=1)

    def __repr__(self):
        return "<Category(title='{}', order='{}')>" \
            .format(self.title, self.order)


class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True)
    image_paths = Column(ARRAY(String))
    thumbnail_image_path = Column(String)
    description = Column(String)
    published = Column(DateTime, nullable=False)
    removed = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete='SET NULL'))

    def __repr__(self):
        return "<Article(title='{}', url='{}' published={})>" \
            .format(self.title, self.url, self.published)
