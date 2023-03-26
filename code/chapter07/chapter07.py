class Movie:
    def __init__(self, title, genre):
        self.title = title
        self.genre = genre
        self.year = year
        self.actors = actors

class MovieFilter:
    def __init__(self, genre):
        self.genre = genre

    def filter(self, movies):
        return [movie for movie in movies if movie.genre == self.genre]
    
class MovieFilterYear:
    def __init__(self, year):
        self.year = year

    def filter(self, movies):
        return [movie for movie in movies if movie.year == self.year]
    
class MovieFilterActors:
    def __init__(self, actors):
        self.actors = actors.split(",") if actors else []

    def filter(self, movies):
        return [movie for movie in movies if all(actor.title() in map(str.title, movie.actors) for actor in self.actors)]

class MovieCollection:
    def __init__(self, movies):
        self.movies = movies

    def filter(self, filter_obj):
        return filter_obj.filter(self.movies)

#daftar film
movies = [
    Movie("The Dark Knight", "Action", 2008, ["Christian Bale", "Heath Ledger"]),
    Movie("Inception", "Sci-Fi", 2010, ["Leonardo DiCaprio", "Tom Hardy"]),
    Movie("Avenger", "Action", 2012, ["Robert Downey Jr", "Chris Evans"]),
    Movie("The Matrix", "Action", 2009, ["J. R. R. Tolkien", "Michael Crichton"]),
    Movie("The Lord of the Rings: The Return of the King", "Action", 2010, ["J. R. R. Tolkien", "Michael Crichton"]),
    Movie("The Shawshank Redemption", "Drama", 1994, ["Tim Robbins", "Morgan Freeman"]),
    Movie("The Godfather", "Drama", 1972, ["Marlon Brando", "Al Pacino"]),
    Movie("Pulp Fiction", "Crime", 1994, ["John Travolta", "Samuel L. Jackson"]),
    Movie("Forrest Gump", "Drama", 1994, ["Tom Hanks", "Robin Wright"]),
    Movie("The Matrix", "Sci-Fi", 1999, ["Keanu Reeves", "Carrie-Anne Moss"]),
    Movie("Fight Club", "Drama", 1999, ["Brad Pitt", "Edward Norton"]),
    Movie("The Silence of the Lambs", "Thriller", 1991, ["Anthony Hopkins", "Jodie Foster"]),
    Movie("Goodfellas", "Crime", 1990, ["Robert De Niro", "Ray Liotta"]),
    Movie("The Departed", "Crime", 2006, ["Leonardo DiCaprio", "Matt Damon"]),
    Movie("The Prestige", "Drama", 2006, ["Hugh Jackman", "Christian Bale"]),
    Movie("Interstellar", "Sci-Fi", 2014, ["Matthew McConaughey", "Anne Hathaway"]),
    Movie("La La Land", "Musical", 2016, ["Ryan Gosling", "Emma Stone"]),
    Movie("Joker", "Drama", 2019, ["Joaquin Phoenix", "Robert De Niro"]),
    Movie("Parasite", "Thriller", 2019, ["Song Kang-ho", "Lee Sun-kyun"]),
    Movie("1917", "War", 2019, ["George MacKay", "Dean-Charles Chapman"]),
    Movie("The Social Network", "Drama", 2010, ["Jesse Eisenberg", "Andrew Garfield"]),
    Movie("Get Out", "Horror", 2017, ["Daniel Kaluuya", "Allison Williams"]),
    Movie("Black Panther", "Action", 2018, ["Chadwick Boseman", "Michael B. Jordan"]),
    Movie("Mad Max: Fury Road", "Action", 2015, ["Tom Hardy", "Charlize Theron"])
]

collection = MovieCollection(movies)

print("Daftar kategori genre yang tersedia: Action, Drama, Sci-Fi, Thriller, Horror, Crimes, Romance")
genre = input("Masukkan kategori genre yang diinginkan: ")
while genre not in ["Action", "Drama", "Sci-Fi", "Thriller", "Horror", "Crimes", "Romance"]:
    print("Kategori genre tidak tersedia. Silakan coba lagi.")
    genre = input("Masukkan kategori genre yang ingin difilter: ")

genre_filter = MovieFilter(genre)
filtered_movies = collection.filter(genre_filter)

if len(filtered_movies) == 0:
    print("Tidak ada film yang ditemukan untuk kategori genre tersebut.")
else:
    print(f"Berikut adalah daftar film untuk kategori genre {genre}:")
    for movie in filtered_movies:
        print(movie.title)
   
#Tahun Filter
year = input("Masukkan tahun rilis yang diinginkan: ")
if year:
    while not year.isdigit():
        print("Input tahun rilis tidak valid. Silakan coba lagi.")
        year = input("Masukkan tahun rilis yang diinginkan: ")
    year = int(year)

    movie_filter = MovieFilterYear(year)
    filtered_movies = collection.filter(movie_filter)

#Output Tahun Filter
if len(filtered_movies) == 0:
    print("Tidak ada film yang ditemukan untuk filter tersebut.")
else:
    print(f"Berikut adalah daftar film untuk filter tersebut:")
    for movie in filtered_movies:
        print(f"{movie.title} ({movie.genre}, {movie.year}) dengan aktor {', '.join(movie.actors)}")
        
        #Aktor Filter
actors = input("Masukkan nama aktor yang diinginkan: ")
if actors:
    actors = actors.title()

movie_filter = MovieFilterActors(actors)
filtered_movies = collection.filter(movie_filter)

#Output Actor Filter
if len(filtered_movies) == 0:
    print("Tidak ada film yang ditemukan untuk filter tersebut.")
else:
    print(f"Berikut adalah daftar film untuk filter tersebut:")
    for movie in filtered_movies:
        print(f"{movie.title} ({movie.genre}, {movie.year}) dengan aktor {', '.join(movie.actors)}")
