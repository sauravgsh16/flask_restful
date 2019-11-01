from db import db


class StoreModel(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    # Creates a back ref. Creates a many-to-one relationship
    items = db.relationship('ItemModel', lazy='dynamic')
    # we use lazy=dynamic, so that each time a store is created, sqlalchemy
    # does not look into the ItemModel to find relationships(This is a very expensive op).
    # lazy='dynamic' also changes the items into a 'query builder' object of sqlalchemy
    # If we did not use lazy='dynamic', it would just be a list

    def __init__(self, name):
        self.name = name

    def json(self):
        # since items is a query builder object, we need to use the 'all' method
        return {
            'id': self.id,
            'name': self.name,
            'items': [item.json() for item in self.items.all()]
        }

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
