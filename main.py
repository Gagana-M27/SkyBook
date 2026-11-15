
import csv
import os
from datetime import datetime

# -----------------------------------------
# SKYBOOK - CP-046
# Dynamic-Fare Flight Reservation and
# Waitlist Engine
# -----------------------------------------

FLIGHTS_FILE = "flights.csv"
RESERVATIONS_FILE = "reservations.csv"
WAITLIST_FILE = "waitlist.csv"

FLIGHT_FIELDS = [
    "flight_id", "airline", "origin", "destination",
    "departure", "total_seats", "seats", "base_fare"
]

RESERVATION_FIELDS = [
    "booking_id", "flight_id", "passenger_name",
    "age", "fare", "booking_time"
]

WAITLIST_FIELDS = [
    "waitlist_id", "flight_id", "passenger_name",
    "age", "request_time"
]

DEFAULT_FLIGHTS = [
    {
        "flight_id": "FL101",
        "airline": "Air India",
        "origin": "Bengaluru",
        "destination": "Delhi",
        "departure": "09:00 AM",
        "total_seats": 50,
        "seats": 50,
        "base_fare": 4500
    },
    {
        "flight_id": "FL102",
        "airline": "IndiGo",
        "origin": "Bengaluru",
        "destination": "Mumbai",
        "departure": "11:30 AM",
        "total_seats": 40,
        "seats": 40,
        "base_fare": 3500
    },
    {
        "flight_id": "FL103",
        "airline": "Air India",
        "origin": "Delhi",
        "destination": "Chennai",
        "departure": "02:00 PM",
        "total_seats": 45,
        "seats": 45,
        "base_fare": 5000
    },
    {
        "flight_id": "FL104",
        "airline": "IndiGo",
        "origin": "Mumbai",
        "destination": "Bengaluru",
        "departure": "06:00 PM",
        "total_seats": 35,
        "seats": 35,
        "base_fare": 3200
    }
]

flights = []
reservations = []
waitlist = []


# ---------- CSV FILE HANDLING ----------

def read_csv_file(filename):
    if not os.path.exists(filename):
        return []

    try:
        with open(filename, "r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))
    except (OSError, csv.Error):
        print(f"Warning: Could not read {filename}.")
        return []


def write_csv_file(filename, fields, records):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)
    except OSError:
        print(f"Error: Could not save {filename}.")


def save_all_data():
    write_csv_file(FLIGHTS_FILE, FLIGHT_FIELDS, flights)
    write_csv_file(RESERVATIONS_FILE, RESERVATION_FIELDS, reservations)
    write_csv_file(WAITLIST_FILE, WAITLIST_FIELDS, waitlist)


def load_data():
    global flights, reservations, waitlist

    saved_flights = read_csv_file(FLIGHTS_FILE)

    if saved_flights:
        flights = []
        for item in saved_flights:
            try:
                flights.append({
                    "flight_id": item["flight_id"],
                    "airline": item["airline"],
                    "origin": item["origin"],
                    "destination": item["destination"],
                    "departure": item["departure"],
                    "total_seats": int(item["total_seats"]),
                    "seats": int(item["seats"]),
                    "base_fare": float(item["base_fare"])
                })
            except (KeyError, ValueError):
                print("Warning: An invalid flight record was skipped.")
    else:
        flights = [flight.copy() for flight in DEFAULT_FLIGHTS]

    reservations = read_csv_file(RESERVATIONS_FILE)
    waitlist = read_csv_file(WAITLIST_FILE)

    save_all_data()


# ---------- HELPER FUNCTIONS ----------

def find_flight(flight_id):
    for flight in flights:
        if flight["flight_id"].lower() == flight_id.lower():
            return flight
    return None


def next_id(records, field, prefix, starting_number):
    highest = starting_number - 1

    for record in records:
        value = record.get(field, "")
        if value.startswith(prefix):
            try:
                number = int(value[len(prefix):])
                highest = max(highest, number)
            except ValueError:
                pass

    return f"{prefix}{highest + 1}"


def calculate_fare(flight):
    total = flight["total_seats"]
    available = flight["seats"]

    if total <= 0:
        return flight["base_fare"]

    occupied = total - available
    occupancy = occupied / total

    if occupancy >= 0.75:
        multiplier = 1.30
    elif occupancy >= 0.50:
        multiplier = 1.20
    elif occupancy >= 0.25:
        multiplier = 1.10
    else:
        multiplier = 1.00

    return round(flight["base_fare"] * multiplier, 2)


def get_passenger_details():
    while True:
        name = input("Enter passenger name: ").strip()
        if name:
            break
        print("Name cannot be empty.")

    while True:
        try:
            age = int(input("Enter passenger age: "))
            if 1 <= age <= 120:
                break
            print("Enter a valid age between 1 and 120.")
        except ValueError:
            print("Please enter age as a number.")

    return name, age


# ---------- FLIGHT FUNCTIONS ----------

def display_flights():
    print("\n" + "=" * 75)
    print("                    AVAILABLE FLIGHTS")
    print("=" * 75)

    for flight in flights:
        fare = calculate_fare(flight)
        print(
            f"\nFlight ID    : {flight['flight_id']}"
            f"\nAirline      : {flight['airline']}"
            f"\nRoute        : {flight['origin']} -> {flight['destination']}"
            f"\nDeparture    : {flight['departure']}"
            f"\nSeats left   : {flight['seats']}/{flight['total_seats']}"
            f"\nCurrent fare : Rs. {fare:.2f}"
        )
        print("-" * 45)


def search_flights():
    print("\n--- SEARCH FLIGHTS ---")
    origin = input("Enter departure city: ").strip().lower()
    destination = input("Enter destination city: ").strip().lower()

    matches = [
        flight for flight in flights
        if flight["origin"].lower() == origin
        and flight["destination"].lower() == destination
    ]

    if not matches:
        print("No matching flights found.")
        return

    print("\nMatching flights:")
    for flight in matches:
        print(
            f"{flight['flight_id']} | {flight['airline']} | "
            f"{flight['departure']} | Seats: {flight['seats']} | "
            f"Fare: Rs. {calculate_fare(flight):.2f}"
        )


# ---------- BOOKING FUNCTIONS ----------

def book_flight():
    print("\n--- BOOK A FLIGHT ---")
    flight_id = input("Enter flight ID: ").strip()
    flight = find_flight(flight_id)

    if flight is None:
        print("Invalid flight ID.")
        return

    name, age = get_passenger_details()

    if flight["seats"] <= 0:
        print("\nSorry! This flight is full.")
        choice = input("Would you like to join the waitlist? (yes/no): ")
        if choice.strip().lower() == "yes":
            waitlist_id = next_id(waitlist, "waitlist_id", "WL", 1001)

            waitlist.append({
                "waitlist_id": waitlist_id,
                "flight_id": flight["flight_id"],
                "passenger_name": name,
                "age": age,
                "request_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            save_all_data()
            print(f"You have been added to the waitlist. ID: {waitlist_id}")
        else:
            print("Waitlist request cancelled.")
        return

    fare = calculate_fare(flight)

    print(f"\nCurrent ticket fare: Rs. {fare:.2f}")
    confirm = input("Confirm booking? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Booking cancelled.")
        return

    booking_id = next_id(reservations, "booking_id", "BK", 1001)

    reservations.append({
        "booking_id": booking_id,
        "flight_id": flight["flight_id"],
        "passenger_name": name,
        "age": age,
        "fare": fare,
        "booking_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    flight["seats"] -= 1
    save_all_data()

    print("\nBooking successful!")
    print(f"Booking ID: {booking_id}")
    print(f"Passenger : {name}")
    print(f"Flight    : {flight['flight_id']}")
    print(f"Fare      : Rs. {fare:.2f}")


def view_reservations():
    print("\n--- PASSENGER RESERVATIONS ---")

    if not reservations:
        print("No reservations found.")
        return

    for booking in reservations:
        print(
            f"\nBooking ID : {booking['booking_id']}"
            f"\nPassenger  : {booking['passenger_name']}"
            f"\nAge        : {booking['age']}"
            f"\nFlight     : {booking['flight_id']}"
            f"\nFare       : Rs. {float(booking['fare']):.2f}"
            f"\nBooked on  : {booking['booking_time']}"
        )
        print("-" * 40)


# ---------- WAITLIST FUNCTIONS ----------

def view_waitlist():
    print("\n--- FLIGHT WAITLIST ---")

    if not waitlist:
        print("No passenger waiting.")
        return

    for number, passenger in enumerate(waitlist, start=1):
        print(
            f"\nPosition   : {number}"
            f"\nWaitlist ID: {passenger['waitlist_id']}"
            f"\nPassenger  : {passenger['passenger_name']}"
            f"\nFlight     : {passenger['flight_id']}"
            f"\nRequested  : {passenger['request_time']}"
        )
        print("-" * 40)


def promote_waitlisted_passenger(flight):
    # Find the earliest waiting passenger for this flight.
    for passenger in waitlist:
        if passenger["flight_id"].lower() == flight["flight_id"].lower():
            fare = calculate_fare(flight)
            booking_id = next_id(reservations, "booking_id", "BK", 1001)

            reservations.append({
                "booking_id": booking_id,
                "flight_id": flight["flight_id"],
                "passenger_name": passenger["passenger_name"],
                "age": int(passenger["age"]),
                "fare": fare,
                "booking_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            waitlist.remove(passenger)
            flight["seats"] -= 1

            print("\nA waiting passenger has been promoted!")
            print(f"Passenger : {passenger['passenger_name']}")
            print(f"New booking ID: {booking_id}")
            print(f"Ticket fare: Rs. {fare:.2f}")
            return

    print("No passenger is waiting for this flight.")


# ---------- CANCELLATION FUNCTION ----------

def cancel_booking():
    print("\n--- CANCEL BOOKING ---")
    booking_id = input("Enter booking ID: ").strip()

    booking_to_cancel = None

    for booking in reservations:
        if booking["booking_id"].lower() == booking_id.lower():
            booking_to_cancel = booking
            break

    if booking_to_cancel is None:
        print("Booking ID not found.")
        return

    flight = find_flight(booking_to_cancel["flight_id"])

    reservations.remove(booking_to_cancel)

    if flight:
        flight["seats"] = min(
            flight["total_seats"],
            flight["seats"] + 1
        )

    print("Booking cancelled successfully.")

    if flight and flight["seats"] > 0:
        promote_waitlisted_passenger(flight)

    save_all_data()


# ---------- MAIN MENU ----------

def main():
    load_data()

    print("\n" + "=" * 55)
    print("             WELCOME TO SKYBOOK")
    print("     Dynamic-Fare Flight Reservation System")
    print("=" * 55)

    while True:
        print("\n============== MAIN MENU ==============")
        print("1. View All Flights")
        print("2. Search Flights")
        print("3. Book a Flight")
        print("4. View Reservations")
        print("5. View Waitlist")
        print("6. Cancel Booking")
        print("7. Exit")
        print("=======================================")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            display_flights()
        elif choice == "2":
            search_flights()
        elif choice == "3":
            book_flight()
        elif choice == "4":
            view_reservations()
        elif choice == "5":
            view_waitlist()
        elif choice == "6":
            cancel_booking()
        elif choice == "7":
            save_all_data()
            print("\nThank you for using SkyBook. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()
