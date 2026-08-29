from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Q
from django.contrib import messages
from django.db import IntegrityError
from .models import Student
from datetime import date
import re

def calculate_age(dob):
    today = date.today()

    age = today.year - dob.year

    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    return age


# Home page
def home(request):
    return render(request, 'students/home.html')


# Login view
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Check username and password
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                "Login successful!"
            )

            return redirect("home")

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

            return redirect("login")

    return render(
        request,
        "students/login.html"
    )


# Register view
def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Required fields
        if not username or not password or not confirm_password:
            messages.error(
                request,
                "All fields are required."
            )
            return redirect("register")

        # Username length
        if len(username) < 3:
            messages.error(
                request,
                "Username must be at least 3 characters long."
            )
            return redirect("register")

        # Password length
        if len(password) < 8:
            messages.error(
                request,
                "Password must be at least 8 characters long."
            )
            return redirect("register")

        # Password confirmation
        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )
            return redirect("register")

        # Import User model
        from django.contrib.auth.models import User

        # Check username
        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Username already exists."
            )
            return redirect("register")

        # Create user
        User.objects.create_user(
            username=username,
            password=password
        )

        messages.success(
            request,
            "Registration successful! Please login."
        )

        return redirect("login")

    return render(
        request,
        "students/register.html"
    )

# Logout view
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


# Display all students + Search
@login_required
def student_list(request):
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "name")

    students = Student.objects.all()

    # Search
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(course__icontains=query) |
            Q(department__icontains=query)
        )

    # Sorting
    if sort == "course":
        students = students.order_by("course", "name")

    elif sort == "department":
        students = students.order_by("department", "name")

    else:
        students = students.order_by("name")

    # Pagination
    paginator = Paginator(students, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "students/student_list.html",
        {
            "students": page_obj,
            "page_obj": page_obj,
            "query": query,
            "sort": sort,
        }
    )




# Add a new student
@login_required
def add_student(request):
    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        date_of_birth = request.POST.get("date_of_birth", "").strip()
        gender = request.POST.get("gender", "").strip()
        address = request.POST.get("address", "").strip()
        course = request.POST.get("course", "").strip()
        department = request.POST.get("department", "").strip()

        # Required fields validation
        if not name or not email or not phone or not date_of_birth or not gender or not address or not course or not department:
            messages.error(request, "All fields are required.")
            return redirect("add_student")

        # Name validation
        if not re.match(r'^[A-Za-z ]+$', name):
            messages.error(
                request,
                "Name should contain only letters and spaces."
            )
            return redirect("add_student")

        # Email validation
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

        if not re.match(email_pattern, email):
            messages.error(
                request,
                "Please enter a valid email address."
            )
            return redirect("add_student")

        # Phone validation
        if not re.match(r'^[6-9]\d{9}$', phone):
            messages.error(
                request,
                "Phone number must be a valid 10-digit number starting with 6, 7, 8 or 9."
            )
            return redirect("add_student")

        # Date of birth validation
        try:
            dob = date.fromisoformat(date_of_birth)

            if dob > date.today():
                messages.error(
                    request,
                    "Date of birth cannot be a future date."
                )
                return redirect("add_student")

            age = calculate_age(dob)

            if age < 5:
                messages.error(
                    request,
                    "Student must be at least 5 years old."
                )
                return redirect("add_student")

        except ValueError:
            messages.error(
                request,
                "Please enter a valid date of birth."
            )
            return redirect("add_student")

        # Address validation
        if len(address) < 5:
            messages.error(
                request,
                "Address must be at least 5 characters long."
            )
            return redirect("add_student")

        # Course validation
        allowed_courses = [
            "MCA",
            "MBA",
            "MCom",
            "MSC",
            "BSC",
            "BCA",
            "BBA",
            "BCom",
            "Other"
        ]

        if course not in allowed_courses:
            messages.error(
                request,
                "Please select a valid course."
            )
            return redirect("add_student")

        # Department validation
        allowed_departments = [
            "Computer Science",
            "Information Technology",
            "Computer Applications",
            "Commerce",
            "Management",
            "Other"
        ]

        if department not in allowed_departments:
            messages.error(
                request,
                "Please select a valid department."
            )
            return redirect("add_student")

        # Gender validation
        allowed_genders = [
            "Male",
            "Female",
            "Other"
        ]

        if gender not in allowed_genders:
            messages.error(
                request,
                "Please select a valid gender."
            )
            return redirect("add_student")

        # Duplicate email
        if Student.objects.filter(email=email).exists():
            messages.error(
                request,
                "This email address is already registered."
            )
            return redirect("add_student")

        # Duplicate phone
        if Student.objects.filter(phone=phone).exists():
            messages.error(
                request,
                "This phone number is already registered."
            )
            return redirect("add_student")

        # Create student
        try:
            Student.objects.create(
                name=name,
                email=email,
                phone=phone,
                date_of_birth=date_of_birth,
                gender=gender,
                address=address,
                course=course,
                department=department
            )

            messages.success(
                request,
                "Student added successfully!"
            )

            return redirect("student_list")

        except IntegrityError:
            messages.error(
                request,
                "Unable to add student. Please check your details."
            )
            return redirect("add_student")

    return render(
        request,
        "students/add_student.html"
    )




# Edit an existing student
@login_required
def edit_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        date_of_birth = request.POST.get("date_of_birth", "").strip()
        gender = request.POST.get("gender", "").strip()
        address = request.POST.get("address", "").strip()
        course = request.POST.get("course", "").strip()
        department = request.POST.get("department", "").strip()

        # Required fields validation
        if not name or not email or not phone or not date_of_birth or not gender or not address or not course or not department:
            messages.error(request, "All fields are required.")
            return redirect("edit_student", id=id)

        # Name validation
        if not re.match(r'^[A-Za-z ]+$', name):
            messages.error(
                request,
                "Name should contain only letters and spaces."
            )
            return redirect("edit_student", id=id)

        # Email validation
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

        if not re.match(email_pattern, email):
            messages.error(
                request,
                "Please enter a valid email address."
            )
            return redirect("edit_student", id=id)

        # Phone validation
        if not re.match(r'^[6-9]\d{9}$', phone):
            messages.error(
                request,
                "Phone number must be a valid 10-digit number starting with 6, 7, 8 or 9."
            )
            return redirect("edit_student", id=id)

        # Date of birth validation
        try:
            dob = date.fromisoformat(date_of_birth)

            if dob > date.today():
                messages.error(
                    request,
                    "Date of birth cannot be a future date."
                )
                return redirect("edit_student", id=id)

            age = calculate_age(dob)

            if age < 5:
                messages.error(
                    request,
                    "Student must be at least 5 years old."
                )
                return redirect("edit_student", id=id)

        except ValueError:
            messages.error(
                request,
                "Please enter a valid date of birth."
            )
            return redirect("edit_student", id=id)

        # Address validation
        if len(address) < 5:
            messages.error(
                request,
                "Address must be at least 5 characters long."
            )
            return redirect("edit_student", id=id)

        # Course validation
        allowed_courses = [
            "MCA",
            "MBA",
            "MCom",
            "MSC",
            "BSC",
            "BCA",
            "BBA",
            "BCom",
            "Other"
        ]

        if course not in allowed_courses:
            messages.error(
                request,
                "Please select a valid course."
            )
            return redirect("edit_student", id=id)

        # Department validation
        allowed_departments = [
            "Computer Science",
            "Information Technology",
            "Computer Applications",
            "Commerce",
            "Management",
            "Other"
        ]

        if department not in allowed_departments:
            messages.error(
                request,
                "Please select a valid department."
            )
            return redirect("edit_student", id=id)

        # Gender validation
        allowed_genders = [
            "Male",
            "Female",
            "Other"
        ]

        if gender not in allowed_genders:
            messages.error(
                request,
                "Please select a valid gender."
            )
            return redirect("edit_student", id=id)

        # Duplicate email
        if Student.objects.filter(
            email=email
        ).exclude(id=id).exists():

            messages.error(
                request,
                "This email address is already registered."
            )
            return redirect("edit_student", id=id)

        # Duplicate phone
        if Student.objects.filter(
            phone=phone
        ).exclude(id=id).exists():

            messages.error(
                request,
                "This phone number is already registered."
            )
            return redirect("edit_student", id=id)

        # Update student
        student.name = name
        student.email = email
        student.phone = phone
        student.date_of_birth = date_of_birth
        student.gender = gender
        student.address = address
        student.course = course
        student.department = department

        student.save()

        messages.success(
            request,
            "Student updated successfully."
        )

        return redirect("student_list")

    return render(
        request,
        "students/edit_student.html",
        {"student": student}
    )
    


# View student details
@login_required
def student_detail(request, id):
    student = get_object_or_404(Student, id=id)

    return render(
        request,
        'students/student_detail.html',
        {'student': student}
    )


# Dashboard view
@login_required
def dashboard(request):

    # Total number of students
    total_students = Student.objects.count()

    # Total number of different courses
    total_courses = (
        Student.objects
        .values('course')
        .distinct()
        .count()
    )

    # Students count for each course
    course_counts = (
        Student.objects
        .values('course')
        .annotate(total=Count('id'))
        .order_by('course')
    )

    # Students count for each department
    department_counts = (
        Student.objects
        .values('department')
        .annotate(total=Count('id'))
        .order_by('department')
    )

    return render(
        request,
        'students/dashboard.html',
        {
            'total_students': total_students,
            'total_courses': total_courses,
            'course_counts': course_counts,
            'department_counts': department_counts,
        }
    )

# Delete a student
@login_required
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == "POST":
        student.delete()

        messages.success(
            request,
            "Student deleted successfully."
        )

        return redirect("student_list")

    return render(
        request,
        "students/delete_student.html",
        {"student": student}
    )