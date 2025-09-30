from django.contrib import admin
from .models import *

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'trainer', 'price', 'is_active')
    list_filter = ('category', 'trainer', 'is_active')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration', 'order')
    list_filter = ('course',)

@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'completed')
    list_filter = ('course', 'completed')

@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'video', 'completed', 'watched_time')
    list_filter = ('completed',)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('student', 'video', 'trainer', 'rating', 'created_at')
    list_filter = ('rating',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'amount', 'payment_status', 'created_at')
    list_filter = ('payment_status',)