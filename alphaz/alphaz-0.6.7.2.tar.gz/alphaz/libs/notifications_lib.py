from ..models.database.users_definitions import Notification, User

def add_notifications(api,db,element_type,element_action,id,users=None,all_users=True):
    user = api.get_logged_user()
    if all_users:
        users       = db.select(User,distinct=User.id,columns=[User.id],filters=[User.id != user["id"]])

    notifications   = [Notification(user=x.id,user_from=user["id"],element_type=element_type,element_action=element_action,element_id=id) for x in users]
    db.add(notifications)