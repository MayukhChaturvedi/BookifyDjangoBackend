# library/management/commands/populate_embeddings.py
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer
from library.mongodb import books_col  # Import the function, not a variable

class Command(BaseCommand):
    help = 'Populate summary_vector field in books collection with embeddings'

    def handle(self, *args, **options):
        # Get the books collection
        # books_col = get_mongo_collection('books')  # Use the function to get the collection
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Fetch books with a summary field
        books = books_col.find({'summary': {'$exists': True}})  # .find() for querying
        for book in books:
            summary = book['summary']
            embedding = model.encode(summary).tolist()
            books_col.update_one(
                {'_id': book['_id']},
                {'$set': {'summary_vector': embedding}}
            )
        self.stdout.write(self.style.SUCCESS('Embeddings populated successfully'))