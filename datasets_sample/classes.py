class event:
    def __init__(self, artist, date, number_of_places, initial_price, city, event_id):
        '''This init method initializes an event object by assigning its artist, date, initial price, total number of places,
        city, and event identifier while also setting the available places equal to the total number of places.'''
        self.artist = artist
        self.date = date
        self.initial_price = initial_price
        self.number_of_places = number_of_places
        self.available_places = number_of_places
        self.city = city
        self.event_id = event_id

    def available_tickets(self, tickets):
        '''Initializes a flag to later indicate whether any ticket is already “On sale” (i.e. available for resale).
        Sets an initially high value to store the lowest resale ticket price found during iteration.
        Initializes a variable to record the identifier (ticket number) of the ticket with the lowest resale price.
        Initializes a variable meant to track the first available “Not sold yet” ticket.'''
        ticket_to_resale = False
        lower_resale_ticket_price = 1000000
        lower_ticket_id = 0
        first_new_ticket = 0

        '''Loops through ticket numbers from 1 up to the total number of places (inclusive), 
            where each iteration inspects one ticket.'''
        for i in range(1, (self.number_of_places + 1)):
            if tickets[f"{self.event_id}-{i}"].status == "Not sold yet" or tickets[f"{self.event_id}-{i}"].status == "On sale":
                if tickets[f"{self.event_id}-{i}"].status == "On sale":
                    ticket_to_resale = True

                '''For each ticket, checks if its status is either unsold or on sale, 
                meaning it’s available for a potential purchase or resale action.'''
                if ticket_to_resale == True:
                    if tickets[f"{self.event_id}-{i}"].price < lower_resale_ticket_price:
                        lower_resale_ticket_price = tickets[f"{self.event_id}-{i}"].price
                        lower_ticket_id = i

                '''Sets the flag indicating that there is at least one ticket available on resale.'''
                if tickets[f"{self.event_id}-{i}"].status == "Not sold yet" and first_new_ticket == 0:
                    first_new_ticket = i

        '''Compares the current ticket’s price with the stored lowest resale price.
        If the current price is lower, updates the lowest resale price 
        Records the current ticket’s number as having the lowest resale price so far.
        
        Checks if the ticket is unsold and ensures that first_new_ticket isn’t still at its initial value
        Stores the current ticket number as the first available unsold ticket.
        
        
        After iterating through all tickets, if there’s a resale ticket and its price is lower than the initial price: 
        Executes a purchase on that ticket for “New owner.” • elif first_new_ticket != 0:
        If no qualifying resale ticket was bought but there is an available unsold ticket
        If no new tickets are available but a ticket is on resale (even if not meeting the price condition earlier): 
        Purchases the resale ticket with the lowest price.
        If none of the conditions above are met, meaning no ticket is available in any form:
        Prints a message indicating that there are no tickets left to buy
        '''
        if ticket_to_resale == True and lower_resale_ticket_price < self.initial_price:
            tickets[f"{self.event_id}-{lower_ticket_id}"].buy_ticket("New owner")

        elif first_new_ticket != 0:
            tickets[f"{self.event_id}-{first_new_ticket}"].buy_ticket("New owner")

        elif ticket_to_resale == True:
            tickets[f"{self.event_id}-{lower_ticket_id}"].buy_ticket("New owner")

        else:
            print("No more tickets are available")

class ticket(event):
    def __init__(self, artist, date, initial_price, id):
        '''This block defines the constructor for the ticket object. It takes parameters for artist, date, initial_price,
        and id, then sets the object's attributes accordingly: the artist and date are stored; both the initial_price and
        current price are set to the provided initial_price; the ticket's status is marked as "Not sold yet";
        the owner is set to None (indicating no owner yet); and the unique identifier is stored.'''
        self.artist = artist
        self.date = date
        self.initial_price = initial_price
        self.price = initial_price
        self.status = "Not sold yet"
        self.owner = None
        self.id = id

    '''This block defines a method to purchase the ticket. It first checks if the ticket's status is not "Sold". 
    If the ticket is available, it assigns the provided new owner to the ticket and updates its status to "Sold"; 
    otherwise, it prints a message stating that the ticket is not on sale.'''
    def buy_ticket(self, new_owner):
        if self.status != "Sold":
            self.owner = new_owner
            self.status = "Sold"
        else:
            print("The ticket is not on sale")

    '''This block defines a method for putting a sold ticket back on sale at a specified price. 
    It first checks if the ticket is in the "Sold" state; if so, it verifies that the new price does not exceed 10% more 
    than the initial_price. If the condition is met, it updates the ticket's price and changes its status to "On sale". 
    If the price is too high, it prints a corresponding warning. 
    Additionally, if the ticket has never been sold ("Not sold yet") or is already on sale, it prints an appropriate 
    message for each case.'''
    def put_on_sales(self, price):
        if self.status == "Sold":
            if price <= (1.1 * self.initial_price):
                self.price = price
                self.status = "On sale"
            else:
                print("The sell price cannot exceed more than 10% the initial price")
        elif self.status == "Not sold yet":
            print("The ticket is not sold yet")
        else:
            print("The ticket is already on sell")