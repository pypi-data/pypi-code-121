from cerberus.dtos.User import User

class UserMapper():

    def mapToUser(ksmUser):
        user = User(ksmUser.getId(),ksmUser.getCreatedAt(), ksmUser.getUpdatedAt())
        return user
