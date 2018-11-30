from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

engine = create_engine(r'sqlite:///Tensorview.db')
Base = declarative_base()

# Declare mapping
class Experiment(Base):
    __tablename__ = 'Experiment'
    eid = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

class Run(Base):
    __tablename__ = 'Run'
    eid = Column(Integer, primary_key=True, nullable=False)
    rid = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

class HyperParameter(Base):
    __tablename__ = 'HyperParameter'
    eid = Column(Integer, primary_key=True, nullable=False)
    rid = Column(Integer, primary_key=True, nullable=False)

# Create a session
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

# Add changes here
d = Experiment(name="Test1")
s = session()
s.add(d)
s.commit()
print(s.query(Experiment).all())

