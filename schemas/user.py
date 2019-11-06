from marshmallow import pre_dump

from ma import ma

from models.user import UserModel

class UserSchema(ma.ModelSchema):
    class Meta:
        # Link UserModel to marshmallow
        model = UserModel
        # Tells marshmallow, specific field for only for loading or dumping data
        load_only = ('password',)
        dump_only = ('id', 'confirmation')

    # pre_dump is a decorator which gets called, before the dump call.
    # We use this, because, in-cases where the use requests for multiple confirmations,
    # all the confirmation will be returned.
    # But we just want the most recent confirmation to be returned.
    # So we change the user.confirmation to be a list of the most recent confirmation
    # Thus, _pre_dump receives the model created, we update the model and then return it.
    # Also, has post_dump, pre_load, post_load etc etc
    @pre_dump
    def _pre_dump(self, user: UserModel):
        user.confirmation = [user.most_recent_confirmation]
        return user
