from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Video, StudentCourse, VideoProgress, Rating, Payment
from .forms import CourseForm
from django.db.models import Sum, Avg
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def course_list(request):
    courses = Course.objects.filter(is_active=True)
    if request.user.user_type == 'student':
        enrolled_courses = StudentCourse.objects.filter(student=request.user).values_list('course_id', flat=True)
        courses = courses.exclude(id__in=enrolled_courses)
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = False
    progress_data = None

    if request.user.user_type == 'student':
        is_enrolled = StudentCourse.objects.filter(student=request.user, course=course).exists()
        if is_enrolled:
            total_videos = course.videos.count()
            completed_videos = VideoProgress.objects.filter(
                student=request.user,
                video__course=course,
                completed=True
            ).count()
            progress_percentage = (completed_videos / total_videos * 100) if total_videos > 0 else 0
            progress_data = {
                'completed': completed_videos,
                'total': total_videos,
                'percentage': progress_percentage
            }

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'progress_data': progress_data
    })


@login_required
def enroll_course(request, course_id):
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('course_list')

    course = get_object_or_404(Course, id=course_id)


    if StudentCourse.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('course_detail', course_id=course_id)


    if course.videos.count() == 0:
        messages.warning(request, 'This course has no videos yet. Please check back later.')
        return redirect('course_detail', course_id=course_id)


    payment = Payment.objects.create(
        student=request.user,
        course=course,
        amount=course.price,
        stripe_payment_intent_id=f"PAY_{request.user.id}_{course.id}",
        payment_status='completed'
    )


    StudentCourse.objects.create(student=request.user, course=course)
    messages.success(request, f'Successfully enrolled in {course.title}')
    return redirect('course_detail', course_id=course_id)


@login_required
def watch_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)


    if not StudentCourse.objects.filter(student=request.user, course=video.course).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('course_list')


    progress, created = VideoProgress.objects.get_or_create(
        student=request.user,
        video=video
    )

    if request.method == 'POST' and 'completed' in request.POST:
        progress.completed = True
        progress.save()
        messages.success(request, 'Video marked as completed!')
        return redirect('watch_video', video_id=video_id)


    next_video = Video.objects.filter(
        course=video.course,
        order__gt=video.order
    ).order_by('order').first()


    ratings = Rating.objects.filter(video=video)


    total_videos = video.course.videos.count()
    completed_videos = VideoProgress.objects.filter(
        student=request.user,
        video__course=video.course,
        completed=True
    ).count()
    progress_percentage = (completed_videos / total_videos * 100) if total_videos > 0 else 0

    return render(request, 'courses/watch_video.html', {
        'video': video,
        'progress': progress,
        'next_video': next_video,
        'ratings': ratings,
        'completed_videos': completed_videos,
        'total_videos': total_videos,
        'progress_percentage': progress_percentage
    })


@login_required
def rate_video(request, video_id):
    if request.method == 'POST':
        video = get_object_or_404(Video, id=video_id)
        rating_value = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')

        rating, created = Rating.objects.update_or_create(
            student=request.user,
            video=video,
            defaults={'rating': rating_value, 'comment': comment}
        )

        messages.success(request, 'Thank you for your rating!')
        return redirect('watch_video', video_id=video_id)


@login_required
def rate_trainer(request, trainer_id):
    if request.method == 'POST':
        from users.models import CustomUser
        trainer = get_object_or_404(CustomUser, id=trainer_id, user_type='trainer')
        rating_value = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')

        rating, created = Rating.objects.update_or_create(
            student=request.user,
            trainer=trainer,
            defaults={'rating': rating_value, 'comment': comment}
        )

        messages.success(request, 'Thank you for rating the trainer!')
        return redirect('trainer_details', trainer_id=trainer_id)


@login_required
def trainer_details(request, trainer_id):
    from users.models import CustomUser
    trainer = get_object_or_404(CustomUser, id=trainer_id, user_type='trainer')
    courses = Course.objects.filter(trainer=trainer, is_active=True)
    return render(request, 'courses/trainer_details.html', {
        'trainer': trainer,
        'courses': courses
    })



@login_required
def trainer_dashboard(request):

    if request.user.user_type != 'trainer' and not request.user.is_staff:
        messages.error(request, 'Access denied. Trainer access required.')
        return redirect('dashboard')

    try:

        my_courses = Course.objects.filter(trainer=request.user)


        courses_data = []
        total_students_count = 0

        for course in my_courses:

            student_count = StudentCourse.objects.filter(course=course).count()
            total_students_count += student_count

            courses_data.append({
                'course': course,
                'student_count': student_count
            })

        context = {
            'is_trainer': True,
            'courses_data': courses_data,
            'total_courses': len(courses_data),
            'total_students': total_students_count
        }

        return render(request, 'trainer/dashboard.html', context)

    except Exception as e:

        context = {
            'is_trainer': True,
            'courses_data': [],
            'total_courses': 0,
            'total_students': 0,
            'error': str(e)
        }
        return render(request, 'trainer/dashboard.html', context)


@login_required
def course_students(request, course_id):
    if request.user.user_type != 'trainer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    course = get_object_or_404(Course, id=course_id, trainer=request.user)


    enrollments = StudentCourse.objects.filter(course=course).select_related('student')


    print(f"DEBUG: Course: {course.title}")
    print(f"DEBUG: Enrollments count: {enrollments.count()}")

    student_progress = []

    for enrollment in enrollments:

        total_videos = course.videos.count()
        completed_videos = VideoProgress.objects.filter(
            student=enrollment.student,
            video__course=course,
            completed=True
        ).count()

        progress_percentage = (completed_videos / total_videos * 100) if total_videos > 0 else 0

        student_progress.append({
            'student': enrollment.student,
            'enrolled_at': enrollment.enrolled_at,
            'completed': enrollment.completed,
            'progress_percentage': progress_percentage,
            'completed_videos': completed_videos,
            'total_videos': total_videos,
            'time_spent': 0,  # Simplified for now
            'last_activity': enrollment.enrolled_at
        })

    context = {
        'course': course,
        'student_progress': student_progress,
        'total_students': len(student_progress),
        'average_progress': sum([p['progress_percentage'] for p in student_progress]) / len(
            student_progress) if student_progress else 0,
        'completed_count': sum(1 for p in student_progress if p['completed']),
        'avg_time_spent': 0
    }

    return render(request, 'courses/course_students.html', context)


@login_required
def add_video(request, course_id):
    if request.user.user_type != 'trainer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    course = get_object_or_404(Course, id=course_id, trainer=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        duration = request.POST.get('duration')
        order = request.POST.get('order', 0)
        video_file = request.FILES.get('video_file')

        if title and duration:
            video = Video.objects.create(
                course=course,
                title=title,
                description=description,
                duration=duration,
                order=order,
                video_file=video_file if video_file else None
            )
            messages.success(request, 'Video added successfully!')
            return redirect('trainer_dashboard')
        else:
            messages.error(request, 'Please fill all required fields.')

    return render(request, 'courses/add_video.html', {'course': course})



@login_required
def manager_dashboard(request):
    if request.user.user_type != 'manager':
        messages.error(request, 'Access denied. Manager only.')
        return redirect('dashboard')

    from users.models import CustomUser
    from courses.models import Course, Payment, Rating


    total_courses = Course.objects.count()
    total_students = CustomUser.objects.filter(user_type='student').count()
    total_trainers = CustomUser.objects.filter(user_type='trainer').count()


    recent_payments = Payment.objects.select_related('student', 'course').order_by('-created_at')[:5]
    recent_feedbacks = Rating.objects.select_related('student', 'video', 'trainer').order_by('-created_at')[:5]


    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(Sum('amount'))['amount__sum'] or 0


    courses_without_trainers = Course.objects.filter(trainer__isnull=True)

    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_trainers': total_trainers,
        'total_revenue': total_revenue,
        'recent_payments': recent_payments,
        'recent_feedbacks': recent_feedbacks,
        'courses_without_trainers': courses_without_trainers,
    }

    return render(request, 'manager/dashboard.html', context)


@login_required
def manage_payments(request):
    if request.user.user_type != 'manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    payments = Payment.objects.select_related('student', 'course').all().order_by('-created_at')


    completed_payments = payments.filter(payment_status='completed')
    pending_payments = payments.filter(payment_status='pending')
    failed_payments = payments.filter(payment_status='failed')

    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        new_status = request.POST.get('payment_status')

        try:
            payment = Payment.objects.get(id=payment_id)
            payment.payment_status = new_status
            payment.save()
            messages.success(request, f'Payment status updated to {new_status}')
            return redirect('manage_payments')  # Redirect to refresh the page
        except Payment.DoesNotExist:
            messages.error(request, 'Payment not found')

    context = {
        'payments': payments,
        'completed_payments': completed_payments,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
    }

    return render(request, 'manager/manage_payments.html', context)


@login_required
def manage_courses(request):
    if request.user.user_type != 'manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    courses = Course.objects.select_related('trainer', 'category').all().order_by('-created_at')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully!')
            return redirect('manage_courses')
    else:
        form = CourseForm()

    context = {
        'courses': courses,
        'form': form
    }

    return render(request, 'manager/manage_courses.html', context)


@login_required
def manage_trainers(request):
    if request.user.user_type != 'manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    from users.models import CustomUser

    trainers = CustomUser.objects.filter(user_type='trainer')

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        if username and email and password:
            try:

                if CustomUser.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists.')
                elif CustomUser.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exists.')
                else:

                    trainer = CustomUser.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        user_type='trainer'
                    )
                    messages.success(request, f'Trainer {username} added successfully!')
                    return redirect('manage_trainers')
            except Exception as e:
                messages.error(request, f'Error creating trainer: {str(e)}')
        else:
            messages.error(request, 'Please fill all required fields.')

    return render(request, 'manager/manage_trainers.html', {
        'trainers': trainers
    })


@login_required
def assign_trainer(request, course_id):
    if request.user.user_type != 'manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    course = get_object_or_404(Course, id=course_id)
    from users.models import CustomUser
    trainers = CustomUser.objects.filter(user_type='trainer')

    if request.method == 'POST':
        trainer_id = request.POST.get('trainer_id')
        trainer = get_object_or_404(CustomUser, id=trainer_id, user_type='trainer')

        course.trainer = trainer
        course.save()
        messages.success(request, f'Trainer {trainer.username} assigned to {course.title}')
        return redirect('manager_dashboard')

    return render(request, 'manager/assign_trainer.html', {
        'course': course,
        'trainers': trainers
    })


@login_required
def student_feedbacks(request):
    if request.user.user_type != 'manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')


    video_ratings = Rating.objects.filter(video__isnull=False).select_related('student', 'video', 'video__course')
    trainer_ratings = Rating.objects.filter(trainer__isnull=False).select_related('student', 'trainer')


    video_avg_rating = video_ratings.aggregate(avg=Avg('rating'))['avg'] or 0
    trainer_avg_rating = trainer_ratings.aggregate(avg=Avg('rating'))['avg'] or 0


    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = {
            'video_count': video_ratings.filter(rating=i).count(),
            'trainer_count': trainer_ratings.filter(rating=i).count(),
        }

    context = {
        'video_ratings': video_ratings,
        'trainer_ratings': trainer_ratings,
        'video_avg_rating': video_avg_rating,
        'trainer_avg_rating': trainer_avg_rating,
        'rating_distribution': rating_distribution,
        'total_feedbacks': video_ratings.count() + trainer_ratings.count(),
    }

    return render(request, 'manager/student_feedbacks.html', context)


@login_required
def analyze_student_progress(request):
    if request.user.user_type != 'manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    from users.models import CustomUser
    from courses.models import Course, StudentCourse, VideoProgress


    students = CustomUser.objects.filter(user_type='student')


    student_progress_data = []

    for student in students:

        enrollments = StudentCourse.objects.filter(student=student)
        total_enrollments = enrollments.count()
        completed_courses = enrollments.filter(completed=True).count()


        total_videos_watched = VideoProgress.objects.filter(
            student=student,
            completed=True
        ).count()

        total_videos_assigned = 0
        for enrollment in enrollments:
            total_videos_assigned += enrollment.course.videos.count()

        overall_progress = (total_videos_watched / total_videos_assigned * 100) if total_videos_assigned > 0 else 0


        last_activity = VideoProgress.objects.filter(
            student=student
        ).order_by('-last_watched').first()

        student_progress_data.append({
            'student': student,
            'total_enrollments': total_enrollments,
            'completed_courses': completed_courses,
            'overall_progress': overall_progress,
            'total_videos_watched': total_videos_watched,
            'last_activity': last_activity.last_watched if last_activity else None,
        })


    courses = Course.objects.all()
    course_progress_data = []

    for course in courses:
        total_students = course.studentcourse_set.count()
        completed_students = course.studentcourse_set.filter(completed=True).count()
        avg_progress = 0

        if total_students > 0:
            total_progress = 0
            for enrollment in course.studentcourse_set.all():
                total_videos = course.videos.count()
                completed_videos = VideoProgress.objects.filter(
                    student=enrollment.student,
                    video__course=course,
                    completed=True
                ).count()
                progress = (completed_videos / total_videos * 100) if total_videos > 0 else 0
                total_progress += progress

            avg_progress = total_progress / total_students

        course_progress_data.append({
            'course': course,
            'total_students': total_students,
            'completed_students': completed_students,
            'avg_progress': avg_progress,
        })


    total_students_count = students.count()
    active_students = students.filter(last_login__isnull=False).count()
    total_courses_count = courses.count()
    total_completions = StudentCourse.objects.filter(completed=True).count()

    context = {
        'student_progress_data': student_progress_data,
        'course_progress_data': course_progress_data,
        'total_students_count': total_students_count,
        'active_students': active_students,
        'total_courses_count': total_courses_count,
        'total_completions': total_completions,
    }

    return render(request, 'manager/analyze_progress.html', context)


@login_required
def initiate_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if StudentCourse.objects.filter(student=request.user, course=course).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('course_detail', course_id=course.id)


    if course.price == 0:
        StudentCourse.objects.create(student=request.user, course=course)
        messages.success(request, "Successfully enrolled in the free course!")
        return redirect('course_detail', course_id=course.id)

    try:

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': course.title,
                        'description': course.description,
                    },
                    'unit_amount': int(course.price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                f'/courses/payment/success/?course_id={course.id}'
            ),
            cancel_url=request.build_absolute_uri(
                f'/courses/payment/cancel/?course_id={course.id}'
            ),
            customer_email=request.user.email,
            metadata={
                'course_id': course.id,
                'student_id': request.user.id
            }
        )


        Payment.objects.create(
            student=request.user,
            course=course,
            amount=course.price,
            stripe_payment_intent_id=checkout_session.id,
            payment_status='pending'
        )

        return redirect(checkout_session.url)

    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('course_detail', course_id=course.id)


@login_required
def payment_success(request):
    course_id = request.GET.get('course_id')

    if course_id:
        try:

            payment = Payment.objects.filter(
                student=request.user,
                course_id=course_id,
                payment_status='pending'
            ).order_by('-created_at').first()

            if payment:

                session_id = payment.stripe_payment_intent_id


                session = stripe.checkout.Session.retrieve(session_id)

                if session.payment_status == 'paid':

                    payment.payment_status = 'completed'
                    payment.save()


                    from courses.models import StudentCourse
                    StudentCourse.objects.get_or_create(
                        student=request.user,
                        course_id=course_id
                    )

                    messages.success(request, "Payment successful! You are now enrolled in the course.")
                    return redirect('course_detail', course_id=course_id)
                else:
                    messages.warning(request, "Payment is still processing.")
            else:
                messages.error(request, "No payment record found.")

        except Exception as e:
            messages.error(request, f"Error verifying payment: {str(e)}")

    return render(request, 'payments/success.html')

@login_required
def payment_cancel(request):
    course_id = request.GET.get('course_id')
    messages.info(request, "Payment was cancelled.")
    return redirect('course_detail', course_id=course_id)