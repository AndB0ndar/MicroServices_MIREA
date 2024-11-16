from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey


Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, default="pending") # pending, completed, canceled

