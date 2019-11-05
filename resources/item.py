from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    get_jwt_identity,
    fresh_jwt_required
)
from marshmallow import ValidationError

from schemas.item import ItemSchema
from models.item import ItemModel

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True) # allows schema creation with many items

class Items(Resource):

    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = item_list_schema.dump(ItemModel.find_all())
        if user_id:
            return {'items': items}, 200
        return {
            'items': [item['name'] for item in items],
            'message': 'Login to get more information'
        }


class Item(Resource):

    @jwt_required
    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {'message': 'Item not present'}, 404

    @fresh_jwt_required
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return {'message': 'Item with this name already present'}, 400

        item_json = request.get_json()
        item_json['name'] = name # need to populate the item object with name

        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except:
            return {'message': 'Failed to add item'}, 500
        return item_schema.dump(item), 201

    @jwt_required
    def delete(self, name: str):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Unauthorized access'}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'Item has been successfully deleted'}, 200
        return {'message': 'Item not found'}, 404

    def put(self, name: str):
        item_json = request.get_json()

        item = ItemModel.find_by_name(name)
        if item:
            item.price = item_json['price']
        else:
            item_json['name'] = name
            item = item_schema.load(item_json)

        item.save_to_db()
        return item_schema.dump(item), 200
