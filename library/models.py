# from django.db import models
# from django.contrib.auth.models import User

# class Author(models.Model):
#     first_name = models.CharField(max_length=100)
#     family_name = models.CharField(max_length=100)
#     date_of_birth = models.DateField(null=True, blank=True)
#     date_of_death = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.first_name} {self.family_name}"

# class Genre(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name

# class Book(models.Model):
#     title = models.CharField(max_length=255)
#     author = models.ForeignKey(Author, on_delete=models.CASCADE)
#     summary = models.TextField()
#     isbn = models.CharField(max_length=13, unique=True)
#     genre = models.ManyToManyField(Genre)

#     def __str__(self):
#         return self.title

# class BookInstance(models.Model):
#     STATUS_CHOICES = [
#         ('Available', 'Available'),
#         ('Maintenance', 'Maintenance'),
#         ('Loaned', 'Loaned'),
#         ('Reserved', 'Reserved'),
#     ]
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     imprint = models.CharField(max_length=255)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Maintenance')
#     due_back = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.book.title} - {self.status}"
