from django.contrib import admin

from common.models import Country, Currency, FeeRate

admin.site.register(Country)
admin.site.register(FeeRate)
admin.site.register(Currency)
