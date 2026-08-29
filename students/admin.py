from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'email',
        'phone',
        'date_of_birth',
        'gender',
        'course',
        'department'
    )

    search_fields = (
        'name',
        'email',
        'phone',
        'course',
        'department'
    )

    list_filter = (
        'gender',
        'course',
        'department'
    )