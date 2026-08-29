from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.login_view, name='login'),

    path('register/', views.register_view, name='register'),

    path('logout/', views.logout_view, name='logout'),

    path('students/', views.student_list, name='student_list'),

    path('add/', views.add_student, name='add_student'),

    path('edit/<int:id>/', views.edit_student, name='edit_student'),

    path('delete/<int:id>/', views.delete_student, name='delete_student'),

    path('student/<int:id>/', views.student_detail, name='student_detail'),

    path('dashboard/', views.dashboard, name='dashboard'),
]