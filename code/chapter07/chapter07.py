class Movie:
    def __init__(self, title, genre):
        self.title = title
        self.genre = genre

class MovieFilter:
    def __init__(self, genre):
        self.genre = genre

    def filter(self, movies):
        return [movie for movie in movies if movie.genre == self.genre]

class MovieCollection:
    def __init__(self, movies):
        self.movies = movies

    def filter(self, filter_obj):
        return filter_obj.filter(self.movies)

movies = [
    Movie("The Dark Knight", "Action"),
    Movie("Inception", "Sci-Fi"),
    Movie("The Godfather", "Drama"),
    Movie("The Shawshank Redemption", "Drama"),
    Movie("The Matrix", "Sci-Fi"),
    Movie("The Silence of the Lambs", "Thriller"),
    Movie("Pulp Fiction", "Crimes"),
    Movie("The Shining", "Horror"),
    Movie("Goodfellas", "Crimes"),
    Movie("Fight Club", "Drama"),
    Movie("Titanic", "Romance"),
    Movie("Casablanca", "Romance"),
    Movie("The Terminator", "Sci-Fi"),
    Movie("Avenger", "Action"),
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
