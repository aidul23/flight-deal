import time

from datetime import datetime, timedelta
import requests

from data_manager import DataManager
from flight_data import find_cheapest_flight
from flight_search import FlightSearch
from notification_manager import NotificationManager

data_manager = DataManager()
sheet_data = data_manager.get_destination_data()
flight_search = FlightSearch()
notification_manager = NotificationManager()


ORIGIN_CITY_IATA = "HEL"

for row in sheet_data:
    if row["iataCode"] == "" or row["iataCode"] == "Not Found":
        row["iataCode"] = flight_search.get_destination_code(row["city"])
        time.sleep(2)
print(f"sheet_data:\n {sheet_data}")

data_manager.destination_data = sheet_data
data_manager.update_destination_codes()

## Customer Email
customer_data = data_manager.get_customer_emails()
print(customer_data)
# Verify the name of your email column in your sheet. Yours may be different from mine
customer_email_list = [row["email"] for row in customer_data]

## Search Flight
tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6*30))

for destination in sheet_data:
    print(f"Getting flights for {destination['city']}...")
    flights = flight_search.check_flights(ORIGIN_CITY_IATA,
                                          destination["iataCode"],
                                          from_time= tomorrow,
                                          to_time= six_month_from_today)

    cheapest_flight = find_cheapest_flight(flights)
    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        # Customise the message depending on the number of stops
        if cheapest_flight.stops == 0:
            message = f"Low price alert! Only GBP {cheapest_flight.price} to fly direct " \
                      f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, " \
                      f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}."
        else:
            message = f"Low price alert! Only GBP {cheapest_flight.price} to fly " \
                      f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, " \
                      f"with {cheapest_flight.stops} stop(s) " \
                      f"departing on {cheapest_flight.out_date} and returning on {cheapest_flight.return_date}."

        print(f"Check your email. Lower price flight found to {destination['city']}!")

        # notification_manager.send_sms(message_body=message)
        # SMS not working? Try whatsapp instead.
        notification_manager.send_whatsapp(message_body=message)

        # Send emails to everyone on the list
        notification_manager.send_emails(email_list=customer_email_list, email_body=message)

