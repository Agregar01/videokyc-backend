from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **other_fields):

        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff set to True.")

        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser set to True.")
        

        return self.create_user(email=email, password=password, **other_fields)
