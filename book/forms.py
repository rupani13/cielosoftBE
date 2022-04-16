from django import forms
from .models import Chapter

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ('chapter_no', 'chapter_name', 'chapter_url', 'book_id')