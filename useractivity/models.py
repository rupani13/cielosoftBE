from django.db import models
from book.models import Books
from account.models import Account
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class UserActivity(models.Model):
    
    user_id                 = models.ForeignKey(Account, on_delete=models.CASCADE, default=1)
    book_id                 = models.ForeignKey(Books, on_delete=models.CASCADE, default=1)
    logged_in_time          = models.TimeField(auto_now=True)
    date                    = models.DateField(auto_now=True)
    chapter                 = models.PositiveIntegerField(null=True, blank=True, default=1)
    unlocked_chapter        = models.BooleanField

    def __str__(self):
        return str(self.date)

class UserFeedback(models.Model):
    email = models.EmailField(max_length=255)
    name = models.CharField(max_length=30,null=True, blank=True)
    comment = models.TextField()
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0),
                                       MaxValueValidator(5)])
    def __str__(self):
        return str(self.name)