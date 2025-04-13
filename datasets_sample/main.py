from data import *
from classes import *

# Creation of an empty dictionary for the events
events = {}

# Loop that create an event instance for each combination of artist-place and insert them in the event disctionary
for artist in concert:
    for i in range(0, len(concert[artist])):
        events[f"{artist}-{concert[artist][i]["Place"]}"] = event(artist, concert[artist][i]["Date"], 10000,
                                                                  concert[artist][i]["Price"], concert[artist][i]["Place"],
                                                                  f"{artist}-{concert[artist][i]["Place"]}")
# Creation of an empty dictionary for the tickets
tickets = {}

# Loop that create an event instance for each combination of artist-place and insert them in the ticket disctionary
for i in events:
    for j in range(1, events[i].number_of_places+1):
        tickets[f"{events[i].artist}-{events[i].city}-{j}"] = ticket(events[i].artist, events[i].date,
                                                                     events[i].initial_price, j)

#Test case
print("Initial situation")
print(f"Ticket with id 1 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-1"].status}")
print(f"Ticket with id 2 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-2"].status}")
print(f"Ticket with id 3 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-3"].status}\n")

print("Selling a ticket")
events["Taylor Swift-Milan"].available_tickets(tickets)
print(f"Ticket with id 1 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-1"].status}")
print(f"Ticket with id 2 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-2"].status}")
print(f"Ticket with id 3 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-3"].status}\n")

print("Selling a second ticket")
events["Taylor Swift-Milan"].available_tickets(tickets)
print(f"Ticket with id 1 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-1"].status}")
print(f"Ticket with id 2 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-2"].status}")
print(f"Ticket with id 3 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-3"].status}\n")

print("Put a ticket on resale with a price more than 10% higher than the initial price (not allowed)")
tickets["Taylor Swift-Milan-1"].put_on_sales(100)
print("\n")

print("Put a ticket on resale with a price lower than initial price")
tickets["Taylor Swift-Milan-1"].put_on_sales(88)
print(f"Ticket 1 status: {tickets["Taylor Swift-Milan-1"].status}")
print(f"Ticket 1 price: {tickets["Taylor Swift-Milan-1"].price}\n")

print("Selling a ticket")
events["Taylor Swift-Milan"].available_tickets(tickets)
print(f"Ticket with id 1 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-1"].status}")
print(f"Ticket with id 2 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-2"].status}")
print(f"Ticket with id 3 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-3"].status}\n")


print("Put a ticket on resale with a price higher than initial price")
tickets["Taylor Swift-Milan-1"].put_on_sales(92)
print(f"Ticket 1 status: {tickets["Taylor Swift-Milan-1"].status}")
print(f"Ticket 1 price: {tickets["Taylor Swift-Milan-1"].price}\n")

print("Selling a ticket")
events["Taylor Swift-Milan"].available_tickets(tickets)
print(f"Ticket with id 1 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-1"].status}")
print(f"Ticket with id 2 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-2"].status}")
print(f"Ticket with id 3 for the Taylor Swift concert in Milan: {tickets["Taylor Swift-Milan-3"].status}\n")

print("Buy a specific ticket")
tickets["Taylor Swift-Milan-1"].buy_ticket("Claudio")
print(f"Ticket 1 status: {tickets["Taylor Swift-Milan-1"].status}")
print(f"Ticket 1 owner: {tickets["Taylor Swift-Milan-1"].owner}")
