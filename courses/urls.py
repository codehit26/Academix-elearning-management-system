from django.urls import path
from . import views

urlpatterns = [

    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('video/<int:video_id>/', views.watch_video, name='watch_video'),
    path('video/<int:video_id>/rate/', views.rate_video, name='rate_video'),
    path('trainer/<int:trainer_id>/rate/', views.rate_trainer, name='rate_trainer'),
    path('trainer/<int:trainer_id>/', views.trainer_details, name='trainer_details'),


    path('trainer/dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    path('trainer/course/<int:course_id>/students/', views.course_students, name='course_students'),
    path('trainer/course/<int:course_id>/add-video/', views.add_video, name='add_video'),


    path('manager/payments/', views.manage_payments, name='manage_payments'),
    path('manager/courses/', views.manage_courses, name='manage_courses'),
    path('manager/trainers/', views.manage_trainers, name='manage_trainers'),
    path('manager/assign-trainer/<int:course_id>/', views.assign_trainer, name='assign_trainer'),
    path('manager/feedbacks/', views.student_feedbacks, name='student_feedbacks'),
    path('manager/analyze-progress/', views.analyze_student_progress, name='analyze_progress'),


    path('payment/<int:course_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
]