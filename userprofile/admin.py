from django.contrib import admin
from userprofile.models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'coins', 'user_id')

admin.site.register(UserProfile, UserProfileAdmin)
