import random
import classes
# Creation of 2 list: one with 10 singers and one with 10 cities
artists = ["Taylor Swift", "The Weekend", "Bad Bunny", "Drake", "Billie Eilish", "Travis Scott", "Peso Pluma",
           "Kanye West", "Ariana Grande", "Feid"]
cities = ["Paris", "Madrid", "Milan", "Zurich", "Berlin", "London", "Amsterdam", "Bruessels", "Dublin", "Varsovia"]

# Creation of an empty dictionary
concert = {}

# Loop that iterate over the artist list
for artist in artists:
    # Add to the dictionary an empty list for each artist
    concert[artist] = []
    # Loop that iterate over the cities
    for city in cities:
        # Create random event variable for each city
        event = {
            "Place": city,
            "Date": f"{random.randint(1, 28)}.{random.randint(1, 12)}.202{random.randint(5, 8)}",
            "Price": (random.randint(8, 15) * 10)
        }
        # Insert this new event in the list artist list
        concert[artist].append(event)

# Print the generated variables
print(concert)