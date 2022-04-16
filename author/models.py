from django.db import models
from django_countries.fields import CountryField
from account.models import Account
# Create your models here.
class Author(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    book_count              = models.IntegerField(default=0)
    app_id                  = models.BigIntegerField
    profilepicture          = models.ImageField(upload_to = 'static/profile', default = '')
    hobbies                 = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.account.name
    