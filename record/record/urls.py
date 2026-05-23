"""
URL configuration for record project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('main_page/', views.main_page, name='main_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('classroom/', views.classroom, name='classroom'),
    path('attendance/', views.attendance, name='attendance'),
    path('schedule/', views.schedule, name='schedule'),
    path('logout/', views.logout_view, name='logout'),
    path('save-classroom/', views.save_classroom, name='save_classroom'),
    path('delete-classroom/<int:id>/', views.delete_classroom, name='delete_classroom'),
    path('update-classroom/<int:id>/', views.update_classroom, name='update_classroom'),
    path('save-student/', views.save_student, name='save_student'),
    path("update-student/<int:id>/", views.update_student, name="update_student"),
    path("delete-student/<int:id>/", views.delete_student, name="delete_student"),
    path('save-activity/', views.save_activity, name='save_activity'),
    path('get-activities/<int:class_id>/<str:term>/', views.get_activities, name='get_activities'),
    path('delete-activity/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('get-activity-students/<int:activity_id>/', views.get_activity_students),
    path('save-activity-scores/<int:activity_id>/', views.save_activity_scores),
    path('get-student-activities/<int:student_id>/', views.get_student_activities),
    path("get-events/", views.get_events, name="get_events"),
    path("add-event/", views.add_event, name="add_event"),
    path("delete-event/", views.delete_event, name="delete_event"),
    path("upcoming-events/", views.upcoming_events, name="upcoming_events"),
    path('get-students/<int:class_id>/', views.get_students, name='get_students'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('get-attendance/<int:class_id>/<str:period>/', views.get_attendance),
    path("get-session/<int:session_id>/", views.get_session),
    path("delete-session/<int:session_id>/", views.delete_session),
    path('update-attendance/<int:session_id>/', views.update_attendance, name='update_attendance'),
    path('get-student-attendance/<int:student_id>/<int:classroom_id>/', views.get_student_attendance),
    path('get-student-grades/<int:student_id>/<int:classroom_id>/', views.get_student_grades),
    path('class-attendance-summary/<int:classroom_id>/',views.get_class_attendance_summary),
    path('class-student-count/<int:class_id>/', views.class_student_count),
    path('dashboard-stats/', views.dashboard_stats),
    path('dashboard-top-students/', views.dashboard_top_students),
    path('dashboard-attendance-analytics/', views.dashboard_attendance_analytics),
    path('dashboard/top-students/', views.dashboard_top_students),
    path('dashboard/get-top-students/', views.get_top_students),
]
