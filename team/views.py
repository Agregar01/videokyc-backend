from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from team.models import Team, TeamMember
from team.serializers import SetPasswordSerializer, TeamMemberInviteSerializer, TeamMemberSerializer, TeamSerializer
from django.contrib.auth.backends import ModelBackend


class TeamView(generics.CreateAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    permission_classes = [permissions.IsAuthenticated,]


class InviteTeamMemberView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = TeamMemberInviteSerializer

    def post(self, request, *agrs, **kwargs):
        serializer = self.serializer_class(data = request.data, context={'request': request})
        if serializer.is_valid():
            business = self.request.user
            serializer.save(business=business)
            return Response({"status": True, "email_sent": True, "message": "An invitation has been sent to this email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(generics.GenericAPIView):
    serializer_class = SetPasswordSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'True', "message": "Password successfully set"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamManagementView(generics.GenericAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        team = self.kwargs.get("team_id")
        team_members = TeamMember.objects.filter(team=team)
        return Response({"status": True, "data": TeamMemberSerializer(team_members, many=True).data})
    
    def destroy(self, request, *args, **kwargs):
        team = self.kwargs.get("team_id")
        team_member_id = self.kwargs.get("team_member_id")
        try:
            team_member = TeamMember.objects.filter(id=team_member_id, team=team)
            team_member.delete()
            return Response({"status": True, "message": "Team member deleted successfully"})
        except TeamMember.DoesNotExist:
            return Response({"status": False, "message": "Team member not found"}, status=404)



