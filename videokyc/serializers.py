from rest_framework import serializers
from videokyc.models import ImageComparison
from rest_framework.response import Response

from videokyc.validators import Validators

validators = Validators
class SendEmailSerializer(serializers.ModelSerializer):
    submitted_image = serializers.FileField(required=True)
    verification_status = serializers.ReadOnlyField()
    callback_url = serializers.URLField(required=False)
    phone = serializers.CharField(
        max_length=100,
        validators=[validators.phone_validation],
    )
    api_key = serializers.CharField(required=False)
    date_of_birth = serializers.CharField(required=True)
    client_id = serializers.CharField(required=True)
    # video = serializers.FileField(required=False)

    def create(self, validated_data):
        return ImageComparison.objects.create(**validated_data)

    class Meta:
        fields = ["id", "type", "description", "external_id", "phone", "email", "submitted_image", "verification_status", "callback_url", "initiator", "reference", "firstname", "lastname", "othernames", "address", "date_of_birth", "api_key", "client_id"]
        model = ImageComparison



class CompleteVerficationSerializer(serializers.ModelSerializer):
    video_image = serializers.FileField(required=True)
    id = serializers.CharField()
    video_verification_start_time = serializers.CharField(required=True)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if instance.video_image:
            representation['video_image'] = request.build_absolute_uri(instance.video_image.url)
        else:
            representation['video_image'] = None

        if instance.submitted_image:
            representation['submitted_image'] = request.build_absolute_uri(instance.submitted_image.url)
        else:
            representation['submitted_image'] = None

        return representation

    class Meta:
        fields = ["id", "video_image", "submitted_image", "longitude", "latitude", "video_verification_start_time"]
        model = ImageComparison


class GetVerficationsSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        if obj.othernames:
            fullname = f"{obj.firstname} {obj.othernames} {obj.lastname}"
        else:
            fullname = f"{obj.firstname} {obj.lastname}"
        
        return fullname
    class Meta:
        model = ImageComparison
        fields = ["email", "phone", "created_at", "reference", "verification_status", "fullname"]

        
class VerficationDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageComparison
        fields = "__all__"