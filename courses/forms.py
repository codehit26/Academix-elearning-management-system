from django import forms
from .models import Course, Video

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'trainer', 'price', 'duration']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'video_file', 'duration', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }