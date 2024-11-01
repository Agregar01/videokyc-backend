from datetime import datetime
from rest_framework import serializers
from authentication import validators
from authentication.models import Business, User
from common.services import CommonUserServices, email_notification
from team.models import Team, TeamMember


common = CommonUserServices


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ["id", "name", "business"]

class TeamMemberInviteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = TeamMember
        fields = ['email', 'team']

    def create(self, validated_data):
        email = validated_data['email']
        team_id = validated_data['team']

        user_id = self.context.get('request').user.id
        user = common.get_user_by_id(user_id)
        if isinstance(user, dict) and not user["status"]:
            return team_member
        business= Business.objects.filter(user=user_id).first()
        team = Team.objects.filter(business=business).first()
        if not team:
            raise serializers.ValidationError('Team does not exist.')
        if team.id != team_id.id:

            raise serializers.ValidationError('You cannot invite a member to a team that does not belong to your business.')

        if TeamMember.objects.filter(email__iexact=email, team=team, is_active=True).exists():
            raise serializers.ValidationError('This user is already a member of the team.')

        team_member = TeamMember.objects.create(
            user=user,
            email=email,
            team=team,
            is_active=False,
        )
        url = f"http://127.0.0.1:8000/team/{team.id}/user/{team_member.id}/"
        message = {
            "subject": f"{team.business.business_name} Account Invitation",
            "content": f"You have been invited to join your team's account. Follow the link to create your password. {url}"
        }
        email_notification(message["subject"], message["content"], email)
        return team_member


class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validators.password_validator])

    def create(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            team_member = TeamMember.objects.filter(email=email).first()
            if not team_member:
                raise serializers.ValidationError('Team member does not exist')
            if team_member and team_member.is_active:
                raise serializers.ValidationError('Team member already exist')
            user = User.objects.create(email=team_member.email, is_primary_account=False)
            user.set_password(password)
            user.save()
            team_member.is_active = True
            team_member.date_joined=datetime.now()
            team_member.save()
        except TeamMember.DoesNotExist:
            raise serializers.ValidationError('Invalid email or the account is already active.')

        team_member.is_active = True
        team_member.save()

        return data


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ["id", "email", "is_active", "date_joined"]