from django.contrib import admin
from useractivity.models import UserActivity, UserFeedback

# Register your models here.
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = [fields.name for fields in UserActivity._meta.get_fields()][1:]

class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'rating')

admin.site.register(UserFeedback, UserFeedbackAdmin)