import os
import json
# import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from bson.objectid import ObjectId
from django.conf import settings
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from pydantic import BaseModel
from .mongodb import authors_col, books_col, genres_col, book_instances_col
from .serializers import AuthorSerializer, BookSerializer, GenreSerializer, BookInstanceSerializer
from utils import get_db_handle

# logger = logging.getLogger(__name__)
db, client = get_db_handle()

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 🔹 Pydantic Model for MongoDB Query
class MongoQuery(BaseModel):
    collection: str
    query: dict | None = None
    type: str | None = None
    field: str | None = None
    query_text: str | None = None
    limit: int | None = None

# 🔹 CRUD for Authors
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def author_list_create(request):
    if request.method == "GET":
        authors = list(authors_col.find({}))
        return Response(AuthorSerializer(authors, many=True).data)
    elif request.method == "POST":
        data = request.data
        author_id = authors_col.insert_one(data).inserted_id
        return Response({"id": str(author_id), "message": "Author created!"})

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def author_detail(request, author_id):
    author = authors_col.find_one({"_id": ObjectId(author_id)})
    if not author:
        return Response({"error": "Author not found"}, status=404)
    if request.method == "GET":
        return Response(AuthorSerializer(author).data)
    elif request.method == "PUT":
        authors_col.update_one({"_id": ObjectId(author_id)}, {"$set": request.data})
        return Response({"message": "Author updated!"})
    elif request.method == "DELETE":
        authors_col.delete_one({"_id": ObjectId(author_id)})
        return Response({"message": "Author deleted!"})

# 🔹 CRUD for Books
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def book_list_create(request):
    if request.method == "GET":
        books = list(books_col.find({}))
        return Response(BookSerializer(books, many=True).data)
    elif request.method == "POST":
        data = request.data
        if "summary" in data:
            summary = data["summary"]
            data["summary_vector"] = embedding_model.encode(summary).tolist()
        book_id = books_col.insert_one(data).inserted_id
        return Response({"id": str(book_id), "message": "Book created!"})

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def book_detail(request, book_id):
    book = books_col.find_one({"_id": ObjectId(book_id)})
    if not book:
        return Response({"error": "Book not found"}, status=404)
    if request.method == "GET":
        return Response(BookSerializer(book).data)
    elif request.method == "PUT":
        data = request.data
        if "summary" in data:
            data["summary_vector"] = embedding_model.encode(data["summary"]).tolist()
        books_col.update_one({"_id": ObjectId(book_id)}, {"$set": data})
        return Response({"message": "Book updated!"})
    elif request.method == "DELETE":
        books_col.delete_one({"_id": ObjectId(book_id)})
        return Response({"message": "Book deleted!"})

# 🔹 CRUD for Genres
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def genre_list_create(request):
    if request.method == "GET":
        genres = list(genres_col.find({}))
        return Response(GenreSerializer(genres, many=True).data)
    elif request.method == "POST":
        data = request.data
        genre_id = genres_col.insert_one(data).inserted_id
        return Response({"id": str(genre_id), "message": "Genre created!"})

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def genre_detail(request, genre_id):
    genre = genres_col.find_one({"_id": ObjectId(genre_id)})
    if not genre:
        return Response({"error": "Genre not found"}, status=404)
    if request.method == "GET":
        return Response(GenreSerializer(genre).data)
    elif request.method == "PUT":
        genres_col.update_one({"_id": ObjectId(genre_id)}, {"$set": request.data})
        return Response({"message": "Genre updated!"})
    elif request.method == "DELETE":
        genres_col.delete_one({"_id": ObjectId(genre_id)})
        return Response({"message": "Genre deleted!"})

# 🔹 CRUD for Book Instances
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def book_instance_list_create(request):
    if request.method == "GET":
        instances = list(book_instances_col.find({}))
        return Response(BookInstanceSerializer(instances, many=True).data)
    elif request.method == "POST":
        data = request.data
        instance_id = book_instances_col.insert_one(data).inserted_id
        return Response({"id": str(instance_id), "message": "Book instance created!"})

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def book_instance_detail(request, instance_id):
    instance = book_instances_col.find_one({"_id": ObjectId(instance_id)})
    if not instance:
        return Response({"error": "Book instance not found"}, status=404)
    if request.method == "GET":
        return Response(BookInstanceSerializer(instance).data)
    elif request.method == "PUT":
        book_instances_col.update_one({"_id": ObjectId(instance_id)}, {"$set": request.data})
        return Response({"message": "Book instance updated!"})
    elif request.method == "DELETE":
        book_instances_col.delete_one({"_id": ObjectId(instance_id)})
        return Response({"message": "Book instance deleted!"})

# 🔹 LangChain Setup for MongoDB Query Generation
def get_mongo_query_chain():
    template = """
    You are a MongoDB query generator. Based on the examples below, convert the user's natural language query into a MongoDB query in JSON format. Respond only with the JSON object, without any additional text or explanation.

    Examples:
    1. Natural language: Get all books by author John Doe
       MongoDB query: {{"collection": "books", "query": {{"author": "John Doe"}}}}

    2. Natural language: Find available book instances of book titled "Adventure Time"
       MongoDB query: {{"collection": "bookinstances", "query": {{"book": "Adventure Time", "status": "Available"}}}}

    3. Natural language: Find books with summaries about mystery
       MongoDB query: {{"collection": "books", "type": "vector_search", "field": "summary", "query_text": "mystery", "limit": 5}}

    Now, convert this query:
    Natural language: {query}
    MongoDB query:
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(model="gemma2-9b-it", temperature=0, api_key=os.getenv('GROQ_API_KEY'))
    parser = PydanticOutputParser(pydantic_object=MongoQuery)
    return prompt | llm | parser

def generate_mongo_query(query):
    """Generate a MongoDB query from a natural language query using LangChain and Groq."""
    chain = get_mongo_query_chain()
    try:
        query_dict = chain.invoke({"query": query})
        if query_dict.collection not in ["books", "authors", "genres", "bookinstances"]:
            raise ValueError(f"Invalid collection name: {query_dict.collection}")
        return query_dict.dict()
    except Exception as e:
        raise ValueError(f"Failed to generate valid MongoDB query: {str(e)}")

def execute_query(query_dict):
    """Execute the generated MongoDB query."""
    collection_name = query_dict['collection']
    collection = db[collection_name]
    
    if 'type' in query_dict and query_dict['type'] == 'vector_search':
        field = query_dict['field']
        query_text = query_dict['query_text']
        limit = query_dict.get('limit', 5)
        if collection_name != "books" or field != "summary":
            raise ValueError("Vector search is only supported for books.summary")
        try:
            query_embedding = embedding_model.encode(query_text).tolist()
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": f"{field}_vector",
                        "queryVector": query_embedding,
                        "limit": limit,
                        "numCandidates": limit * 10
                    }
                }
            ]
            result = list(collection.aggregate(pipeline))
            return result
        except Exception as e:
            raise Exception(f"Vector search failed: {str(e)}")
    else:
        return list(collection.find(query_dict['query'] or {}))
    
def format_data(data):
    """Format retrieved data as a JSON string, filtering relevant fields."""
    filtered_data = [
        {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc.items() if k in ["title", "summary", "status"]}
        for doc in data
    ]
    data_str = json.dumps(filtered_data, default=str)
    return data_str

def generate_response(query, data_str):
    """Generate a natural language response from the query and data using Groq, formatted as Markdown."""
    response_prompt = """
    Based on the following query and data, provide a natural language response formatted as a Markdown list. 
    Each item should be a bullet point with the book title in bold, followed by a dash and its summary. 
    Start with a brief introductory sentence.

    Examples:
    1. Query: What books are available by author John Doe?
       Data: [{{"title": "Book A", "status": "Available"}}, {{"title": "Book B", "status": "Available"}}]
       Response: Here are the available books by John Doe:
                 - **Book A** - This book is available for checkout.
                 - **Book B** - This book is available for checkout.

    2. Query: Find books about mystery
       Data: [{{"title": "Mystery Book", "summary": "A thrilling mystery novel"}}]
       Response: Here are books related to mystery:
                 - **Mystery Book** - A thrilling mystery novel.

    3. Query: List all genres
       Data: []
       Response: No genres were found in the database.

    Now, for the current query:
    Query: {query}
    Data: {data}
    Response:
    """
    try:
        chat_completion = ChatGroq(
            model="gemma2-9b-it",
            temperature=0,
            api_key=os.getenv('GROQ_API_KEY')
        ).invoke([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": response_prompt.format(query=query, data=data_str)}
        ])
        response = chat_completion.content.strip()
        return response
    except Exception as e:
        raise Exception(f"Response generation failed: {str(e)}")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rag_query(request):
    """Handle natural language queries via the RAG system."""
    query = request.data.get('query')
    if not query:
        return Response({'error': 'Query is required'}, status=400)
    
    try:
        mongo_query = generate_mongo_query(query)
        data = execute_query(mongo_query)
        data_str = format_data(data)
        response = generate_response(query, data_str)
        return Response({'response': response})
    except ValueError as e:
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)