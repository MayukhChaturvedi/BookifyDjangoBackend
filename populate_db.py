import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import random
from faker import Faker
import uuid
from dotenv import load_dotenv
load_dotenv()

# Initialize Faker for realistic data
fake = Faker()

# MongoDB connection (adjust based on your settings)
client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))
db = client[os.environ.get("DB_NAME", "local_library")]

# Collections
authors_col = db['authors']
books_col = db['books']
genres_col = db['genres']
book_instances_col = db['bookinstances']

# Load embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Base data for procedural generation
BASE_AUTHORS = [
    "Agatha Christie", "J.R.R. Tolkien", "Isaac Asimov", "Jane Austen", "Hilary Mantel",
    "Stephen King", "George R.R. Martin", "Arthur C. Clarke", "Charlotte Bronte", "Philip K. Dick"
]

BASE_GENRES = [
    "Mystery", "Fantasy", "Science Fiction", "Romance", "Historical Fiction",
    "Thriller", "Horror", "Adventure", "Drama", "Biography", "Crime", "Dystopian",
    "Young Adult", "Literary Fiction", "Western", "Comedy", "Poetry", "Non-Fiction",
    "Speculative Fiction", "Gothic"
]

SUMMARY_TEMPLATES = {
    "Mystery": ["A detective unravels {0} in {1}.", "A {0} mystery unfolds in {1}."],
    "Fantasy": ["A {0} quests through {1} to {2}.", "Magic and {0} collide in {1}."],
    "Science Fiction": ["A {0} explores {1} in a {2} future.", "Technology shapes {0} on {1}."],
    "Romance": ["Love blossoms between {0} and {1} in {2}.", "A {0} romance unfolds in {1}."],
    "Historical Fiction": ["In {0}, {1} navigates {2}.", "{0} shapes the life of {1} in {2}."],
    "Thriller": ["A {0} races against {1} in {2}.", "Suspense grips {0} amidst {1}."],
    "Horror": ["Terror stalks {0} in {1} due to {2}.", "A {0} faces {1} horrors in {2}."],
    "Adventure": ["A {0} journeys to {1} seeking {2}.", "{0} braves {1} for {2}."]
    # Add more templates for other genres as needed
}

CHARACTERS = ["detective", "princess", "scientist", "soldier", "explorer", "writer", "thief", "king"]
SETTINGS = ["a quiet village", "a distant planet", "a haunted mansion", "Victorian London", "a futuristic city", "a medieval kingdom"]
PLOT_POINTS = ["a hidden treasure", "a dark secret", "a lost civilization", "an ancient curse", "a galactic war"]

STATUSES = ["Available", "Checked Out", "Reserved"]

def clear_collections():
    """Clear existing data from collections."""
    authors_col.delete_many({})
    books_col.delete_many({})
    genres_col.delete_many({})
    book_instances_col.delete_many({})
    print("Collections cleared.")

def populate_authors(num_authors=50):
    """Insert authors into the database."""
    authors = []
    # Start with base authors
    for name in BASE_AUTHORS:
        authors.append({"name": name, "bio": f"{name.split()[1]} is a celebrated author known for {fake.sentence()}"})
    
    # Generate additional authors
    while len(authors) < num_authors:
        name = fake.name()
        if name not in [a["name"] for a in authors]:
            authors.append({"name": name, "bio": f"{name.split()[1]} writes {fake.sentence()}"})
    
    authors_col.insert_many(authors)
    print(f"Inserted {len(authors)} authors.")
    return [a["name"] for a in authors]

def populate_genres(num_genres=20):
    """Insert genres into the database."""
    genres = []
    # Start with base genres
    for name in BASE_GENRES[:num_genres]:
        genres.append({"name": name, "description": f"{name} features {fake.sentence()}"})
    
    genres_col.insert_many(genres)
    print(f"Inserted {len(genres)} genres.")
    return [g["name"] for g in genres]

def populate_books(authors, genres, num_books=300):
    """Insert books with embeddings into the database."""
    books = []
    used_titles = set()
    
    # Generate books
    for _ in range(num_books):
        author = random.choice(authors)
        genre = random.choice(genres)
        title = f"{fake.word().capitalize()} {fake.word().capitalize()}"
        while title in used_titles:  # Ensure unique titles
            title = f"{fake.word().capitalize()} {fake.word().capitalize()}"
        used_titles.add(title)
        
        # Generate summary based on genre
        template = random.choice(SUMMARY_TEMPLATES.get(genre, SUMMARY_TEMPLATES["Mystery"]))
        summary = template.format(
            random.choice(CHARACTERS),
            random.choice(SETTINGS),
            random.choice(PLOT_POINTS)
        )
        
        # Generate embedding
        summary_vector = embedding_model.encode(summary).tolist()
        
        book = {
            "title": title,
            "author": author,
            "summary": summary,
            "genre": genre,
            "summary_vector": summary_vector
        }
        books.append(book)
    
    books_col.insert_many(books)
    print(f"Inserted {len(books)} books.")
    return books

def populate_book_instances(num_instances_target=700):
    """Insert book instances into the database."""
    books = list(books_col.find({}))
    instances = []
    
    for book in books:
        # Aim for 2-3 instances per book, adjusting to hit ~700 total
        num_instances = random.randint(2, 3)
        for _ in range(num_instances):
            if len(instances) >= num_instances_target:
                break
            instance = {
                "book": book["title"],
                "status": random.choice(STATUSES),
                "due_date": fake.date_time_this_year() if random.choice([True, False]) else None
            }
            instances.append(instance)
    
    # If we haven't reached the target, add more instances
    while len(instances) < num_instances_target:
        book = random.choice(books)
        instance = {
            "book": book["title"],
            "status": random.choice(STATUSES),
            "due_date": fake.date_time_this_year() if random.choice([True, False]) else None
        }
        instances.append(instance)
    
    book_instances_col.insert_many(instances)
    print(f"Inserted {len(instances)} book instances.")

def main():
    """Populate all collections with meaningful data."""
    clear_collections()
    authors = populate_authors(50)
    genres = populate_genres(20)
    books = populate_books(authors, genres, 300)
    populate_book_instances(700)
    total_docs = (authors_col.count_documents({}) + 
                  genres_col.count_documents({}) + 
                  books_col.count_documents({}) + 
                  book_instances_col.count_documents({}))
    print(f"Database population complete! Total documents: {total_docs}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()