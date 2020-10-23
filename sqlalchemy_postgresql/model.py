from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

Base = declarative_base()


class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String, unique=True)

    def __repr__(self):
        return "<Source(name='{}')>".format(self.name)


class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    src_url = Column(String, unique=True)
    bdx_url = Column(String, unique=True)
    tags = Column(ARRAY(String))
    published_at = Column(DateTime(timezone=True))
    og_image_url = Column(String)
    og_image_path = Column(String)
    image_urls = Column(ARRAY(String))
    image_paths = Column(ARRAY(String))
    excerpt = Column(String)
    html = Column(String)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete='SET NULL'))

    def __repr__(self):
        return "<Article(title='{}', url='{}' published={})>" \
            .format(self.title, self.src_url, self.published_at)
