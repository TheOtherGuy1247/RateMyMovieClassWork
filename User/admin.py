from django.contrib import admin
from .models import User, Genre, Movie, WatchlistItem

class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}

class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'year']
    prepopulated_fields = {'slug': ('title',)}

class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'added_at']

# Register your models here.
admin.site.register(User)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(WatchlistItem, WatchlistItemAdmin)
