from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
    return render(request, 'home.html')


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    if user.user_type == 'student':
        from courses.models import StudentCourse, VideoProgress
        enrolled_courses = StudentCourse.objects.filter(student=user)
        progress_data = []
        for course_enrollment in enrolled_courses:
            total_videos = course_enrollment.course.videos.count()
            completed_videos = VideoProgress.objects.filter(
                student=user,
                video__course=course_enrollment.course,
                completed=True
            ).count()
            progress_percentage = (completed_videos / total_videos * 100) if total_videos > 0 else 0
            progress_data.append({
                'course': course_enrollment.course,
                'progress': progress_percentage,
                'completed_videos': completed_videos,
                'total_videos': total_videos
            })
        context['progress_data'] = progress_data

    elif user.user_type == 'trainer':
        from courses.models import Course
        courses = Course.objects.filter(trainer=user)
        course_data = []
        for course in courses:
            enrolled_students = course.studentcourse_set.count()
            total_videos = course.videos.count()
            course_data.append({
                'course': course,
                'enrolled_students': enrolled_students,
                'total_videos': total_videos
            })
        context['course_data'] = course_data

    elif user.user_type == 'manager':
        from courses.models import Course, Payment
        from users.models import CustomUser
        total_courses = Course.objects.count()
        total_students = CustomUser.objects.filter(user_type='student').count()
        total_trainers = CustomUser.objects.filter(user_type='trainer').count()
        recent_payments = Payment.objects.select_related('student', 'course').order_by('-created_at')[:10]
        total_revenue = sum([payment.amount for payment in
                             Payment.objects.filter(payment_status='completed')]) if Payment.objects.filter(
            payment_status='completed').exists() else 0

        context.update({
            'total_courses': total_courses,
            'total_students': total_students,
            'total_trainers': total_trainers,
            'recent_payments': recent_payments,
            'total_revenue': total_revenue
        })

    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    user = request.user
    context = {'user': user}

    if user.user_type == 'student':
        from courses.models import StudentCourse
        enrolled_courses = StudentCourse.objects.filter(student=user)
        context['enrolled_courses'] = enrolled_courses

    return render(request, 'users/profile.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.skype_id = request.POST.get('skype_id', '')
        user.whatsapp_number = request.POST.get('whatsapp_number', '')
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return redirect('profile')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)