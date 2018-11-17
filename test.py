from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import Column, ForeignKey, Integer, String
#from sqlalchemy.orm import relationship
#from sqlalchemy import create_engine

app = Flask(__name__)
#Will need to update database url
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\chr14\\tensorview\\test.sql'
db = SQLAlchemy(app)

class e1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    learningrate = db.Column(db.Integer, unique=True, nullable=False)
    momentum = db.Column(db.Integer, unique=True, nullable=False)
    type = db.Column(db.String(120), unique=True, nullable=False)
    accuracy = db.Column(db.Integer, unique=True, nullable=False)

    def __init__(self, id=None, learningrate=None, momentum=None, type=None, accuracy=None):
        self.id = id
        self.learningrate = learningrate
        self.momentum = momentum
        self.type = type
        self.accuracy = accuracy

    def __repr__(self):
        return '<e1 %r>' % self.id

#engine = create_engine('sqlite:///sqlalchemy_example.db')
#Base.metadata.create_all(engine)
