"""college_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path

from main_app.EditResultView import EditResultView

from . import hod_views, staff_views, student_views, views


urlpatterns = [
    # General Views
     path("", views.login_page, name='login_page'),
     path("get_attendance", views.get_attendance, name='get_attendance'),
     path("doLogin/", views.doLogin, name='user_login'),
     path("logout_user/", views.logout_user, name='user_logout'),
     path("check_email_availability", hod_views.check_email_availability, name="check_email_availability"),
     # Admin / HOD Views
     # Dashboard and Profile Management
     path("admin/home/", hod_views.admin_home, name='admin_home'),
     path("admin_view_profile", hod_views.admin_view_profile, name='admin_view_profile'),

     # Staff Management
     path("teacher/add", hod_views.add_staff, name='add_staff'),
     path("teacher/manage/", hod_views.manage_staff, name='manage_staff'),
     path("teacher/edit/<int:staff_id>", hod_views.edit_staff, name='edit_staff'),
     path("teacher/delete/<int:staff_id>", hod_views.delete_staff, name='delete_staff'),
     path('add_staff_csv/', hod_views.add_staff_csv, name='add_staff_csv'),

     # Course and Subject Management
     path("schools/add", hod_views.add_course, name='add_course'),
     path("schools/manage/", hod_views.manage_course, name='manage_course'),
     path("schools/edit/<int:course_id>", hod_views.edit_course, name='edit_course'),
     path("schools/delete/<int:course_id>", hod_views.delete_course, name='delete_course'),

     path("class/add/", hod_views.add_subject, name='add_subject'),
     path("class/manage/", hod_views.manage_subject, name='manage_subject'),
     path("class/edit/<int:subject_id>", hod_views.edit_subject, name='edit_subject'),
     path("class/delete/<int:subject_id>", hod_views.delete_subject, name='delete_subject'),

     # Student Management
     path("student/add/", hod_views.add_student, name='add_student'),
     path("student/manage/", hod_views.manage_student, name='manage_student'),
     path("student/edit/<int:student_id>", hod_views.edit_student, name='edit_student'),
     path("student/delete/<int:student_id>", hod_views.delete_student, name='delete_student'),
     path("delete_students/", hod_views.delete_students, name='delete_students'),

     # Session Management
     path("schedule/add", hod_views.add_session, name='add_session'),
     path("schedule/manage/", hod_views.manage_session, name='manage_session'),
     path("schedule/edit/<int:session_id>", hod_views.edit_session, name='edit_session'),
     path("schedule/delete/<int:session_id>", hod_views.delete_session, name='delete_session'),

     # Notifications
     path("send_student_notification/", hod_views.send_student_notification, name='send_student_notification'),
     path("send_staff_notification/", hod_views.send_staff_notification, name='send_staff_notification'),
     path("admin_notify_student", hod_views.admin_notify_student, name='admin_notify_student'),
     path("admin_notify_staff", hod_views.admin_notify_staff, name='admin_notify_staff'),

     # Feedback and Leave Management
     path("student/view/feedback/", hod_views.student_feedback_message, name="student_feedback_message"),
     path("teacher/view/feedback/", hod_views.staff_feedback_message, name="staff_feedback_message"),
     path("student/view/leave/", hod_views.view_student_leave, name="view_student_leave"),
     path("teacher/view/leave/", hod_views.view_staff_leave, name="view_staff_leave"),

     # Attendance Management
     path("attendance/view/", hod_views.admin_view_attendance, name="admin_view_attendance"),
     path("attendance/fetch/", hod_views.get_admin_attendance, name='get_admin_attendance'),
     path('export_attendance/', hod_views.export_attendance, name='export_attendance'),
     path('delete-attendance/', hod_views.delete_attendance, name='delete_attendance'),

     # Filtering and Loading Data
     path('filter-data-by-date/', hod_views.filter_data_by_date, name='filter_data_by_date'),
     path('ajax/load-classes/', hod_views.load_classes, name='ajax_load_classes'),
     path('ajax/load-classes-student/', hod_views.load_classes_student, name='ajax_load_classes_student'),
     path('get_subjects_by_schedule/', hod_views.get_subjects_by_session, name='get_subjects_by_session'),

     # CSV Import/Export
     path('import_csv/', hod_views.import_csv, name='import_csv'),
     path('import_csv_teaching_schedule/', hod_views.import_csv_teaching_schedule, name='import_csv_teaching_schedule'),

     # Staff-Specific Views
     path("teacher/home/", staff_views.staff_home, name='staff_home'),
     path("teacher/schedule", staff_views.staff_apply_leave, name='staff_apply_leave'),
     path("teacher/feedback/", staff_views.staff_feedback, name='staff_feedback'),
     path("teacher/view/profile/", staff_views.staff_view_profile, name='staff_view_profile'),

     # Attendance for Staff
     path("teacher/attendance/take/", staff_views.staff_take_attendance, name='staff_take_attendance'),
     path("teacher/attendance/update/", staff_views.staff_update_attendance, name='staff_update_attendance'),
     path("teacher/get_students/", staff_views.get_students, name='get_students'),
     path("teacher/attendance/fetch/", staff_views.get_student_attendance, name='get_student_attendance'),
     path("teacher/attendance/save/", staff_views.save_attendance, name='save_attendance'),
     path("teacher/attendance/update/", staff_views.update_attendance, name='update_attendance'),

     # Notifications for Staff
     path("teacher/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
     path("teacher/view/notification/", staff_views.staff_view_notification, name="staff_view_notification"),

     # Results for Staff
     path("teacher/result/add/", staff_views.staff_add_result, name='staff_add_result'),
     path("teacher/result/edit/", EditResultView.as_view(), name='edit_student_result'),
     path('teacher/result/fetch/', staff_views.fetch_student_result, name='fetch_student_result'),

     # QR Code Scanner for Staff
     path('teacher/qr_code_scanner/', staff_views.qr_code_scanner, name='qr_code_scanner'),
     path('complete_teaching_schedule/', staff_views.complete_teaching_schedule, name='complete_teaching_schedule'),
     path('teacher/get_subjects_by_session_teacher/', staff_views.get_subjects_by_session_staff, name='get_subjects_by_session_staff'),

     # Student-Specific Views
     path("student/home/", student_views.student_home, name='student_home'),
     path("student/view/attendance/", student_views.student_view_attendance, name='student_view_attendance'),
     path("student/apply/leave/", student_views.student_apply_leave, name='student_apply_leave'),
     path("student/feedback/", student_views.student_feedback, name='student_feedback'),
     path("student/view/profile/", student_views.student_view_profile, name='student_view_profile'),
     path("student/fcmtoken/", student_views.student_fcmtoken, name='student_fcmtoken'),
     path("student/view/notification/", student_views.student_view_notification, name="student_view_notification"),
     path('student/view/result/', student_views.student_view_result, name='student_view_result'),
]