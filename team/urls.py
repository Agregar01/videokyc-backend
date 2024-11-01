from django.urls import path
from team.views import InviteTeamMemberView, SetPasswordView, TeamManagementView, TeamView


urlpatterns = [
    path("invite-member/", InviteTeamMemberView.as_view(), name="invite-member"),
    path("team-member/set-password/", SetPasswordView.as_view(), name="set-password"),
    path("", TeamView.as_view(), name="create-team"),
    path('<uuid:team_id>/members/<uuid:member_id>/', TeamManagementView.as_view(), name='team-member-management')

]
