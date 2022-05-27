from demo.models import User


def test_user():
    user = User(username="user_name")
    assert str(user) == 'user_name'
    assert user.label == 'user_name'

    user = User(display_name="display_name")
    assert user.label == 'display_name'

    user = User(first_name="first_name")
    assert user.label == 'first_name'

    user = User(first_name="first_name", last_name="last_name")
    assert user.label == 'first_name last_name:'
