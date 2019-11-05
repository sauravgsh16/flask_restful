from ma import ma

from models.store import StoreModel
# We import this, since ItemModel and StoreModel have a relationship
# In case StoreModel does not get imported before ItemModel, it will break
from models.item import ItemModel
from schemas.item import ItemSchema

class StoreSchema(ma.ModelSchema):
    # Tells marshmallow, items is a property on store which are many ItemSchemas
    items = ma.Nested(ItemSchema, many=True)
    class Meta:
        model = StoreModel
        dump_only = ('id',)
