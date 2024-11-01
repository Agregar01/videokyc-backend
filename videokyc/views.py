
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
# from apikeys.models import APIKeys, Account
from videokyc.models import EMAIL_STATUS_CHOICES, VERIFICATION_STATUS_CHOICES, ImageComparison, Link
from videokyc.serializers import SendEmailSerializer, CompleteVerficationSerializer, GetVerficationsSerializer, VerficationDetailSerializer
from rest_framework.response import Response
import calendar
from rest_framework.pagination import PageNumberPagination


from videokyc.utils import get_extra_request_details, get_request_data

# verifier = DeepFaceVerifier


class SendEmail(generics.GenericAPIView):
    serializer_class = SendEmailSerializer
    parser_classes = (FormParser, MultiPartParser)

    @transaction.atomic
    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data = self.request.data)
        serializer.is_valid(raise_exception=True)
        api_key = serializer.validated_data.get("api_key")
        client_id = serializer.validated_data.get("client_id")
        initiator = serializer.validated_data.get("initiator")

        if not api_key and not initiator:
            print("aaa")
            return Response({"status": False, "message": "Either 'api_key' or 'initiator' must be provided"})
    
        if api_key:
            if not APIKeys.objects.filter(key=api_key).first():
                return Response({"status": False, "message": "API Key not found"})
            
        if client_id:
            account = Account.objects.filter(client_id=client_id).first()
            
        if initiator:
            print("mmmmm")
            if not initiator.get("core_user_id"):
                return Response({"status": False, "message": "Business ID missing in request"})


        saved_instance = serializer.save()
        # time_threshold = timezone.now() - timedelta(minutes=60)
        # links = Link.objects.filter(created_at__gte=time_threshold, email=serializer.validated_data["email"])
        # if links.exists():
        #     return Response({"status": False, "message": "A link has already been sent to this email. Links expire after 60 minutes"})

        data = dict(serializer.validated_data)
        url = "https://videokyc.agregartech.com/"
        request_id = saved_instance.id
        email_data = {
            "subject": "Video KYC Verification",
            "message": f"Follow this link to verify your identity: {url}verification/client/{request_id}/",
        }
        link = Link.objects.create(email=serializer.validated_data["email"])
        serializer.save(link_sent_time=link.created_at, email_status=EMAIL_STATUS_CHOICES.DELIVERED.value, client_id = account.client_id)
        common.email_notification(email_data["subject"], email_data["message"], data.get("email"))
        saved_instance.email_status = EMAIL_STATUS_CHOICES.DELIVERED.value
        saved_instance.save()
        return Response({"status": True, "id": saved_instance.id, "message": "Verification email has been sent"})


class VerifyClient(generics.GenericAPIView):
    serializer_class = CompleteVerficationSerializer
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            try:
                # Fetch the existing image comparison record
                image_compare = ImageComparison.objects.filter(id=serializer.validated_data["id"]).first()
                
                if image_compare:
                    # Update the image comparison object with new data
                    image_compare.longitude = serializer.validated_data["longitude"]
                    image_compare.latitude = serializer.validated_data["latitude"]
                    image_compare.video_image = serializer.validated_data["video_image"]
                    image_compare.save()
                    image_compare.refresh_from_db()

                    # Process additional request data
                    get_request_data(request, image_compare)
                    get_extra_request_details(str(image_compare.id))

                    # Compare faces using DeepFaceVerifier
                    # videokyc = DeepFaceVerifier.compare_faces(image_compare.submitted_image.url, image_compare.video_image.url)
                    videokyc = {"status": True}
                    if videokyc.get("status", False):
                        # If face is verified and anti-spoofing check passes
                        if videokyc["comparison"]["verified"] and videokyc["spoof"]["is_real"]:
                            image_compare.verification_status = VERIFICATION_STATUS_CHOICES.MATCH_FOUND
                            response = {
                                "status": True,
                                "reference_id": image_compare.reference,
                                "message": "Verification completed successfully",
                                "is_match": True,
                                "facial_match": videokyc["comparison"]["verified"],
                                "real_image": videokyc["spoof"]["is_real"]
                            }
                        else:
                            # If face verification or anti-spoofing fails
                            image_compare.verification_status = VERIFICATION_STATUS_CHOICES.MATCH_NOT_FOUND
                            response = {
                                "status": True,
                                "reference_id": image_compare.reference,
                                "message": "Verification completed successfully",
                                "is_match": False,
                                "facial_match": videokyc["comparison"]["verified"],
                                "real_image": videokyc["spoof"]["is_real"]
                            }
                        
                        # Finalize the verification process
                        image_compare.video_verification_start_time = serializer.validated_data["video_verification_start_time"]
                        image_compare.verification_completed = True
                        image_compare.video_verification_details = {
                            "verification_id": str(image_compare.id),
                            "verification_details": videokyc,
                        }
                        image_compare.verification_completed_time = datetime.now()
                        image_compare.consent_sorted = True
                        image_compare.save()

                        return Response(response)
                    return Response(videokyc)
                
                return Response({"status": False, "message": "A verification request with this ID does not exist"})
            
            except Exception as e:
                # Handle unexpected exceptions
                return Response({"status": False, "message": str(e)})

        # If serializer validation fails, return errors
        return Response({"status": False, "message": serializer.errors})
        

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 60
    
class GetVerifications(generics.GenericAPIView):
    serializer_class = GetVerficationsSerializer
    queryset = ImageComparison.objects.all()
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):

        client_id = self.kwargs.get("client_id")
        verifications = ImageComparison.objects.filter(client_id=client_id).order_by("-created_at")
        paginator = self.pagination_class()
        paginated_verifications = paginator.paginate_queryset(verifications, request)
        serializer = GetVerficationsSerializer(paginated_verifications, many=True)
        return paginator.get_paginated_response(serializer.data)


def calculate_percentage_change(current_count, previous_count):
    if previous_count == 0:
        return 0  # or return 0 if you prefer that for percentage when there's no data for the previous month
    return ((current_count - previous_count) / previous_count) * 100

class GetVerificationsStatistics(generics.GenericAPIView):
    serializer_class = GetVerficationsSerializer

    def get(self, request, *args, **kwargs):
        client_id = self.kwargs.get("client_id")
        queryset = ImageComparison.objects.filter(client_id=client_id).order_by("-created_at")

        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        _, current_month_end_day = calendar.monthrange(today.year, today.month)
        current_month_end = today.replace(day=current_month_end_day)

        if today.month == 1:
            previous_month_end = today.replace(year=today.year - 1, month=12, day=31)
            previous_month_start = today.replace(year=today.year - 1, month=12, day=1)
        else:
            previous_month = today.month - 1
            _, previous_month_end_day = calendar.monthrange(today.year, previous_month)
            previous_month_start = today.replace(month=previous_month, day=1)
            previous_month_end = today.replace(month=previous_month, day=previous_month_end_day)
        
        current_month_queryset = queryset.filter(created_at__gte=current_month_start, created_at__lte=current_month_end)
        previous_month_queryset = queryset.filter(created_at__gte=previous_month_start, created_at__lte=previous_month_end)
        
        current_month_match = queryset.filter(created_at__gte=current_month_start, created_at__lte=current_month_end).filter(verification_status = VERIFICATION_STATUS_CHOICES.MATCH_FOUND.value)
        previous_month_match = queryset.filter(created_at__gte=previous_month_start, created_at__lte=previous_month_end).filter(verification_status = VERIFICATION_STATUS_CHOICES.MATCH_FOUND.value)

        current_month_mismatch = queryset.filter(created_at__gte=current_month_start, created_at__lte=current_month_end).filter(verification_status = VERIFICATION_STATUS_CHOICES.MATCH_NOT_FOUND.value)
        previous_month_mismatch = queryset.filter(created_at__gte=previous_month_start, created_at__lte=previous_month_end).filter(verification_status = VERIFICATION_STATUS_CHOICES.MATCH_NOT_FOUND.value)

        current_month_pending = queryset.filter(created_at__gte=current_month_start, created_at__lte=current_month_end).filter(verification_status = VERIFICATION_STATUS_CHOICES.PENDING.value)
        previous_month_pending = queryset.filter(created_at__gte=previous_month_start, created_at__lte=previous_month_end).filter(verification_status = VERIFICATION_STATUS_CHOICES.PENDING.value)

        total_change_per_month = calculate_percentage_change(current_month_queryset.count(), previous_month_queryset.count())
        matched_change_per_month = calculate_percentage_change(current_month_match.count(), previous_month_match.count())
        mismatched_change_per_month = calculate_percentage_change(current_month_mismatch.count(), previous_month_mismatch.count())
        pending_change_per_month = calculate_percentage_change(current_month_pending.count(), previous_month_pending.count())


        time_threshold = timezone.now() - timedelta(days=7)
        matched = queryset.filter(verification_status = VERIFICATION_STATUS_CHOICES.MATCH_FOUND.value)
        mismatched = queryset.filter(verification_status = VERIFICATION_STATUS_CHOICES.MATCH_NOT_FOUND.value)
        pending = queryset.filter(verification_status = VERIFICATION_STATUS_CHOICES.PENDING.value)
        total_verifications_count_week = queryset.filter(created_at__gte=time_threshold)
        matched_week = matched.filter(created_at__gte=time_threshold)
        mismatched_week = mismatched.filter(created_at__gte=time_threshold)
        pending_week = pending.filter(created_at__gte=time_threshold)
        
        return Response({
            "status:": True,
            "total_verifications_count": queryset.count(),
            "total_verifications_count_week": total_verifications_count_week.count(),

            "matched_count": matched.count(),
            "mismatched_count": mismatched.count(),
            "pending_count": pending.count(),

            "matched_week_count": matched_week.count(),
            "mismatched_week_count": mismatched_week.count(),
            "pending_week_count": pending_week.count(),

            "total_change_per_month": round(total_change_per_month, 2),
            "matched_change_per_month": round(matched_change_per_month, 2),
            "mismatched_change_per_month": round(mismatched_change_per_month, 2),
            "pending_change_per_month": round(pending_change_per_month, 2),
        })


class GetVerificationsDetail(generics.GenericAPIView):
    serializer_class = VerficationDetailSerializer
    queryset = ImageComparison.objects.all().order_by("-created_at")

    def get(self, request, *args, **kwargs):
        reference_id = kwargs.get('reference_id')
        print(reference_id)
        verification = ImageComparison.objects.filter(reference=reference_id).first()
        print(verification)
        return Response(
            {
                "personal_data": {
                    "candidate_name": f"{verification.firstname} {verification.othernames or ''} {verification.lastname}",
                    "candidate_email": verification.email,
                    "candidate_phone": verification.phone,
                    "candidate_address": verification.address,
                    "candidate_dob": verification.date_of_birth,
                    "candidate_geolocation_coordinates": f"[{verification.longitude}, {verification.latitude}]",
                },
                "verification_records": {
                    "id": str(verification.id),
                    "reference": verification.reference,
                    "link_sent": verification.email_status,
                    "email_sent_time": verification.link_sent_time,
                    "video_verification_start_time": verification.video_verification_start_time,
                    "verification_completed_time": verification.verification_completed_time,
                    "verification_duration": verification.verification_completed_time,
                    "verification_completed": verification.verification_completed,
                    "video_image": verification.video_image.url if verification.video_image else None,
                    "submitted_image": verification.submitted_image.url if verification.submitted_image else None,
                    "consent_sorted": verification.consent_sorted,
                    "type": verification.type,
                },
                "device_information": verification.device_info,
                "sim_swap_verification": verification.sim_swap_details,
                "ofac_search": {
                    "ofac_search_done": True,
                    "ofac_search_match_found": verification.ofac_verification["match"] if verification.ofac_verification and "match" in verification.ofac_verification else False
                },
                "facial_comparison_details": verification.video_verification_details
            }
        )