# myapp/management/commands/check_transactions.py
import time
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from common.services import Statuses
from financials.Ideospay.callback import send_callback
from financials.Ideospay.card import Ideospay
from financials.Ideospay.ideos_utils import IdeospayEncrypt
from financials.models import Transaction, TRANSACTION_STATUS_CODES
from financials.models import ThirdParties
from decouple import config
import json
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Check transaction status and update the database every 5 mins"

    def handle(self, *args, **kwargs):
        while True:
            self.check_transaction_statuses()
            time.sleep(10 * 60)

    def check_transaction_statuses(self):
        print("kkkk")
        filter_range = timezone.now() - timedelta(hours=3)
        url = "https://payment-api-service.ideospaygo.com/payment/order/status"

        transactions = Transaction.objects.exclude(status_code__iexact=Statuses.SUCCESSFUL_STATUS.value).filter(created_at__gt=filter_range)
        for transaction_instance in transactions:
            third_parties = ThirdParties.objects.filter(transaction_id = transaction_instance.id, acquirer="IDEOSPAY").first()
            if third_parties:
                try:
                    print("ccccc")
                    payload = json.dumps({
                        "reference": str(transaction_instance.id)
                    })
                    headers = {
                        "api-key": config("IDEOS_API_KEY"),
                        "Content-Type": "application/json"
                    }
                    encrypted = IdeospayEncrypt.encrypt(payload)
                    data = json.dumps({
                        "data": encrypted
                    })
                    response = requests.request("POST", url, headers=headers, data=data).json()
                    
                    if response["data"]["orderSummary"]["status"] == "Failed":
                        print("faileddddddd")
                        transaction_instance.status_code =Statuses.FAILED_STATUS.value
                        transaction_instance.status_message = Statuses.FAILED_MESSAGE.value
                        third_parties.status_code =Statuses.FAILED_STATUS.value
                        transaction_instance.exception_reason = response["data"]["orderSummary"]["paymentResponseMessage"]
                        transaction_instance.save()
                        third_parties.save()
                        if not transaction_instance.callback_sent:
                            print("xxxxxxxxxxxxx")
                            send_callback(transaction_instance)

                    elif response["data"]["orderSummary"]["status"] == "Successful":
                        print("sucessssssssss")
                        transaction_instance.status_code = Statuses.SUCCESSFUL_STATUS.value
                        transaction_instance.status_message = Statuses.SUCCESSFUL_MESSAGE.value
                        third_parties.status_code = Statuses.SUCCESSFUL_STATUS.value
                        print("saving................")
                        transaction_instance.save()
                        third_parties.save()
                        if not transaction_instance.callback_sent:
                            print("seenoooooooo")
                            send_callback(transaction_instance)

                except Exception as e:
                    print(f"Error occurred for transaction {transaction_instance.id}: str{e}")
        print("saved//////////////////////")
