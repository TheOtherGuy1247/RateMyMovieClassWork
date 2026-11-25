from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q
from django.urls import reverse
# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True, max_length=100)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, default = '', max_length=60)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, default = '', max_length=200)
    year = models.PositiveSmallIntegerField()
    runtime_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    runtime_hour = models.PositiveSmallIntegerField(null=True, blank=True)
    overview = models.TextField(blank=True)
    poster_url = models.ImageField(blank=True, upload_to='movie_posters/')
    trailer_url = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)
    is_featured = models.BooleanField(
        "staff pick", default=False,
        help_text="Show this movie first in “Featured this week” on the homepage.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.year})"

    def get_absolute_url(self):
        return reverse("movie_detail", args=[self.id])

    @property
    def runtime_display(self):
        """148 -> '2h 28m'"""
        if not self.runtime_minutes:
            return ""
        hours, minutes = divmod(self.runtime_minutes, 60)
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"

    @property
    def poster_hue(self):
        """A color (0-359) for the placeholder poster when there is no poster_url."""
        return (self.id * 47) % 360


class Review(models.Model):
    """One user's rating (required) and comment (optional) for one movie."""

    RATING_CHOICES = [
        (1, "1 - Poor"),
        (2, "2 - Fair"),
        (3, "3 - Good"),
        (4, "4 - Very good"),
        (5, "5 - Excellent"),
    ]

    # Every review must belong to a user: the database rejects a review without one.
    # settings.AUTH_USER_MODEL is Django's built-in User (the auth_user table).
    # If a user deletes their account, their reviews are deleted too (CASCADE).
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # One review per user per movie (posting again edits the existing one)
            models.UniqueConstraint(fields=["user", "movie"], name="one_review_per_user_per_movie"),
            # The database itself refuses ratings outside 1-5, even from code that skips the form
            models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=5), name="rating_1_to_5"),
        ]

    def __str__(self):
        return f"{self.user} rated {self.movie.title} {self.rating}/5"

    @property
    def was_edited(self):
        return (self.updated_at - self.created_at).total_seconds() > 1


class WatchlistItem(models.Model):
    """A movie a user saved to watch later."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlist"
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="watchlisted_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "movie"], name="one_watchlist_entry_per_movie"),
        ]

    def __str__(self):
        return f"{self.user} wants to watch {self.movie.title}"
