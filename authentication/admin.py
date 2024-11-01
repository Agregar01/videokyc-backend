from django.contrib import admin

from authentication.models import Business, User

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):

    list_display = (
        "business_name",
        "fullname",
        "email",
        "phone",
        "business_type",
        "is_kyc_submitted",
        "is_approved",
        "created_at",
    )
    list_filter = (
        "is_approved",
        "is_kyc_submitted",
        "business_type",
        "created_at",
    )
    search_fields = ("business_name", "fullname", "email", "phone", "created_at")

    def fullname(self, obj):
        return f"{obj.user.firstname} {obj.user.lastname}"

    def email(self, obj):
        return obj.user.email

    def phone(self, obj):
        return obj.user.phone

    fullname.short_description = 'Full Name'
    email.short_description = 'Email'
    phone.short_description = 'Phone'

admin.site.register(User)