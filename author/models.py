from django.db import models
from django_countries.fields import CountryField
from account.models import Account
# Create your models here.
def author_cloud_upload(instance, file_name):
    file_path = os.path.join('static/profile', file_name)
    return file_path
class Author(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    book_count              = models.IntegerField(default=0)
    app_id                  = models.BigIntegerField
    profilepicture          = models.ImageField(upload_to=author_cloud_upload, default = '', blank=True, null=True)
    hobbies                 = models.TextField(blank=True, null=True)
    intro                   = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.account.name
    
