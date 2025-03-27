from rest_framework import serializers

class AuthorSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    first_name = serializers.CharField(max_length=100)
    family_name = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateField(required=False)
    date_of_death = serializers.DateField(required=False)

class BookSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=255)
    author = serializers.CharField()
    summary = serializers.CharField()
    isbn = serializers.CharField(max_length=13)
    genre = serializers.ListField(child=serializers.CharField(), required=False)

class GenreSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)

class BookInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    book = serializers.CharField()
    imprint = serializers.CharField(max_length=255)
    status = serializers.ChoiceField(choices=["Available", "Maintenance", "Loaned", "Reserved"])
    due_back = serializers.DateField(required=False)
