import requests
import os
from dotenv import load_dotenv

load_dotenv()

SHEET_ENDPOINT_PRICE = os.environ["SHEETY_ENDPOINT"]
SHEET_ENDPOINT_USER = os.environ["SHEETY_USERS_ENDPOINT"]

class DataManager:
    def __init__(self):
        self.destination_data = {}
        self.customer_data = {}

    def get_destination_data(self):
        response = requests.get(url=SHEET_ENDPOINT_PRICE)
        data = response.json()
        self.destination_data = data["prices"]
        return self.destination_data

    def update_destination_codes(self):
        for city in self.destination_data:
            new_data = {
                "price": {
                    "iataCode": city["iataCode"]
                }
            }

            response = requests.put(url=f"{SHEET_ENDPOINT_PRICE}/{city['id']}", json=new_data)
            print(response.text)

    def get_customer_emails(self):
        response = requests.get(url=SHEET_ENDPOINT_USER)
        data = response.json()
        self.customer_data = data["users"]
        return self.customer_data