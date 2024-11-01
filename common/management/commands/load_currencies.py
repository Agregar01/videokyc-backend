from django.core.management.base import BaseCommand, CommandError
import time
import requests
from common.models import Currency


API_KEY = "VXpCb1BNSU5aNUVnV1Rzc3dqanJSb3NtQUZIMUNIbWtUbkFlbmZ3Tw=="  # Not a secret


class Command(BaseCommand):
    help = "Retrieve countries and their currencies and populates the db"

    def get_all_countries(self):
        url = "https://api.countrystatecity.in/v1/countries"
        headers = {"X-CSCAPI-KEY": API_KEY}
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            return True, response.json()
        return False, None

    def get_country_detail(self, country_code: str, session: requests.Session):
        url = f"https://api.countrystatecity.in/v1/countries/{country_code}"
        headers = {"X-CSCAPI-KEY": API_KEY}
        response = session.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        return None

    def handle(self, *args, **kwargs):
        is_success, all_countries = self.get_all_countries()
        request_session = requests.Session()

        if is_success:
            print("Success")

            country_objs = []
            existing_countries = [country.code for country in Currency.objects.all()]
            countries_to_create = [
                country
                for country in all_countries
                if country and country.get("iso2") not in existing_countries
            ]

            for country in countries_to_create:

                country_detail = self.get_country_detail(
                    country.get("iso2"), request_session
                )
                if country_detail:
                    print("Country details...")
                    country_objs.append(
                        Currency(
                            code=country_detail["currency"],
                            name=country_detail["currency_name"],
                        )
                    )

                else:
                    print("breaking...")
                    break
                time.sleep(0.5)
            Currency.objects.bulk_create(country_objs, ignore_conflicts=True)
        else:
            print("Failed")
            pass
