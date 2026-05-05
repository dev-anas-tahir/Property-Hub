from django.contrib.auth import get_user_model

User = get_user_model()


def user_get_by_email(*, email: str) -> User | None:
    return User.objects.filter(email=email).first()
