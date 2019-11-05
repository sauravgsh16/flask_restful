from ma import ma

from models.user import UserModel

class UserSchema(ma.ModelSchema):
    class Meta:
        # Link UserModel to marshmallow
        model = UserModel
        # Tells marshmallow, specific field for only for loading or dumping data
        load_only = ('password',)
        dump_only = ('id',)
