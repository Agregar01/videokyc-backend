from django.db import models
from authentication.models import Business, User
from common.models import BaseModel

class Team(BaseModel):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="team")
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.business.business_name} Team || {self.id}"


class TeamMember(BaseModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    email = models.EmailField()
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.team.business.business_name}"
