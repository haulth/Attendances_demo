from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUserManager(UserManager):
    def _create_user(self, email, student_id, password, **extra_fields):
        if email:
            email = self.normalize_email(email)
            user = CustomUser(email=email, **extra_fields)
        elif student_id:
            user = CustomUser(student_id=student_id, **extra_fields)
        else:
            raise ValueError("Phải cung cấp email hoặc mã học sinh")

        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, student_id=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email=email, student_id=student_id, password=password, **extra_fields)

    def create_superuser(self, email=None, student_id=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser phải có is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser phải có is_superuser=True.")

        return self._create_user(email=email, student_id=student_id, password=password, **extra_fields)

class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return (
            "Từ ngày "
            + self.start_year.strftime("%d/%m/%Y")
            + " đến "
            + self.end_year.strftime("%d/%m/%Y")
        )  
           
class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    GENDER = [("M", "Nam"), ("F", "Nữ")]

    username = None  
    email = models.EmailField(unique=True, null=True, blank=True)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField(null=True, blank=True)
    address = models.TextField()
    # fcm_token = models.TextField(default="")  # Để thông báo firebase
    qr_code = models.ImageField(
        upload_to="QR/", null=True, blank=True
    )  # Thêm trường lưu mã QR
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "student_id"  # Mặc định là student_id
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if self.user_type == "3":  # Student
            self.email = None  # Đặt email là None cho Student
            if not self.student_id:
                raise ValueError("Student ID is required for students")
        else:
            self.student_id = self.student_id  # Đặt student_id là None nếu không phải Student
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Course(models.Model):
    name = models.CharField(max_length=120, null=True) #tên trường
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=False)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name


class Subject(models.Model):
    name = models.CharField(max_length=120) #tên lớp
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=False)
    session = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True) # TÊN lớp học

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name

    
class Attendance(models.Model):
    session = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TeachingSchedule(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    school_name = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Subject, on_delete=models.CASCADE)
    schedule_date = models.DateField()
    start_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lịch dạy của giáo viên {self.staff.admin.first_name} {self.staff.admin.last_name} tại {self.school_name} lớp {self.class_name} vào {self.start_time} giờ ngày {self.schedule_date}"
    def list_class_name(self):
        return self.class_name
    def list_school_name(self):
        return self.school_name


class CompletedTeachingSchedule(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    schedule = models.ForeignKey(TeachingSchedule, on_delete=models.CASCADE) 
    completed_date = models.DateField() 

    def __str__(self):
        return f"Lịch dạy của {self.staff.first_name} {self.staff.last_name} vào {self.schedule.schedule_date}"

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()
