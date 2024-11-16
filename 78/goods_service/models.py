from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Text, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

location_product = Table(
    'location_product',
    Base.metadata,
    Column('location_id', Integer, ForeignKey('locations.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True)
)

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)

    products = relationship('Product', secondary=location_product, back_populates='locations')


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)

    locations = relationship('Location', secondary=location_product, back_populates='products')


