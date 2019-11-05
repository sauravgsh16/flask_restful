from ma import ma

from models.item import ItemModel
# We import this, since ItemModel and StoreModel have a relationship
# In case StoreModel does not get imported before ItemModel, it will break
from models.store import StoreModel

class ItemSchema(ma.ModelSchema):
    class Meta:
        model = ItemModel
        load_only = ('store',)
        dump_only = ('id',)
        include_fk = True # Include foreign_key: don't ignore any properties when dbs are linked
