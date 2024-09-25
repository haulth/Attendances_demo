from django import forms
from django.forms.widgets import DateInput

from .models import *

class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Thay đổi giao diện của các trường
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

class CustomUserForm(FormSettings):
    student_id = forms.CharField(required=True, label="Mã học sinh")  
    email = forms.EmailField(required=True, label="Email")      
    gender = forms.ChoiceField(choices=[('M', 'Nam'), ('F', 'Nữ')], label="Giới tính")
    first_name = forms.CharField(required=True, label="Tên")
    last_name = forms.CharField(required=True, label="Họ")
    address = forms.CharField(widget=forms.Textarea, label="Địa chỉ")
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    profile_pic = forms.ImageField(label="Hình ảnh đại diện")

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if user_type in ['staff', 'admin']:
            self.fields['student_id'].required = False
            self.fields['student_id'].widget = forms.HiddenInput()
           
        else:
            self.fields['email'].required = False
            self.fields['email'].widget = forms.HiddenInput()
            

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'student_id', 'email', 'gender', 'address', 'profile_pic', 'password')

class CustomStaffForm(FormSettings):
    # student_id = forms.CharField(required=True, label="Mã học sinh")  
    email = forms.EmailField(required=True, label="Email")      
    gender = forms.ChoiceField(choices=[('M', 'Nam'), ('F', 'Nữ')], label="Giới tính")
    first_name = forms.CharField(required=True, label="Tên")
    last_name = forms.CharField(required=True, label="Họ")
    address = forms.CharField(widget=forms.Textarea, label="Địa chỉ")
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    profile_pic = forms.ImageField(label="Hình ảnh đại diện")

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super(CustomStaffForm, self).__init__(*args, **kwargs)


    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'gender', 'address', 'profile_pic', 'password')

class CustomAdminForm(FormSettings):
    # student_id = forms.CharField(required=True, label="Mã học sinh")  
    email = forms.EmailField(required=True, label="Email")      
    gender = forms.ChoiceField(choices=[('M', 'Nam'), ('F', 'Nữ')], label="Giới tính")
    first_name = forms.CharField(required=True, label="Tên")
    last_name = forms.CharField(required=True, label="Họ")
    address = forms.CharField(widget=forms.Textarea, label="Địa chỉ",required=False)
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    profile_pic = forms.ImageField(label="Hình ảnh đại diện")

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super(CustomAdminForm, self).__init__(*args, **kwargs)


    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'gender', 'address', 'profile_pic', 'password')
        
class CustomStudentForm(FormSettings):
    student_id = forms.CharField(required=True, label="Mã học sinh")  
    # email = forms.EmailField(required=True, label="Email")      
    gender = forms.ChoiceField(choices=[('M', 'Nam'), ('F', 'Nữ')], label="Giới tính")
    first_name = forms.CharField(required=True, label="Tên")
    last_name = forms.CharField(required=True, label="Họ")
    address = forms.CharField(widget=forms.Textarea, label="Địa chỉ")
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu", required=True)
    # profile_pic = forms.ImageField(label="Hình ảnh đại diện", required=True)

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super(CustomStudentForm, self).__init__(*args, **kwargs)

            

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'student_id', 'gender', 'address','password')


# class StudentForm(CustomStudentForm):
#     course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Chọn trường")
#     session = forms.ModelChoiceField(queryset=Subject.objects.all(), label="Chọn lớp")  
#     class Meta(CustomStudentForm.Meta):
#         model = Student
#         fields = CustomStudentForm.Meta.fields + ('course', 'session')

class StudentForm(CustomStudentForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Chọn trường")
    session = forms.ModelChoiceField(queryset=Subject.objects.none(), label="Chọn lớp")

    def __init__(self, *args, **kwargs):
        # Tách user_type từ kwargs nếu có
        user_type = kwargs.pop('user_type', None)
        super(StudentForm, self).__init__(*args, **kwargs)

        # Cập nhật giao diện của các trường
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

        # Lọc lớp học (session) theo trường (course) qua AJAX
        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                self.fields['session'].queryset = Subject.objects.filter(course_id=course_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Nếu không có giá trị hợp lệ
        elif self.instance.pk and hasattr(self.instance, 'course'):
            self.fields['session'].queryset = self.instance.course.subject_set.order_by('name')

    class Meta(CustomStudentForm.Meta):
        model = Student
        fields = CustomStudentForm.Meta.fields + ('course', 'session')



class AdminForm(CustomAdminForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)


    class Meta(CustomAdminForm.Meta):
        model = Admin
        fields = CustomAdminForm.Meta.fields

class StaffForm(CustomStaffForm):
    # course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Chọn địa điểm dạy")

    class Meta(CustomStaffForm.Meta):
        model = Staff  # Adjust this if you have a different model for staff
        fields = CustomStaffForm.Meta.fields# + ('course',)  # Change ['course'] to ('course',)


class CourseForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Course

class SubjectForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ['name',  'course']

class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }

# class TeachingScheduleForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(TeachingScheduleForm, self).__init__(*args, **kwargs)
#         # Thay đổi giao diện của các trường
#         for field in self.visible_fields():
#             field.field.widget.attrs['class'] = 'form-control'

#     class Meta:
#         model = TeachingSchedule
#         fields = ['staff', 'school_name', 'class_name', 'schedule_date', 'start_time']
#         widgets = {
#             'schedule_date': forms.DateInput(attrs={'type': 'date'}),
#             'start_time': forms.TimeInput(attrs={'type': 'time'}),
            
#         }

class TeachingScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TeachingScheduleForm, self).__init__(*args, **kwargs)

        # Cập nhật giao diện của các trường
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

        # Lọc lớp học (class_name) theo trường (school_name) qua AJAX
        self.fields['class_name'].queryset = Subject.objects.none()

        if 'school_name' in self.data:
            try:
                course_id = int(self.data.get('school_name'))
                self.fields['class_name'].queryset = Subject.objects.filter(course_id=course_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Nếu không có giá trị hợp lệ
        elif self.instance.pk:
            self.fields['class_name'].queryset = self.instance.school_name.subject_set.order_by('name')

    class Meta:
        model = TeachingSchedule
        fields = ['staff', 'school_name', 'class_name', 'schedule_date', 'start_time']
        widgets = {
            'schedule_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
        }
               
class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }

class FeedbackStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']

class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }

class FeedbackStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']

class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields

class StaffEditForm(CustomStaffForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomStaffForm.Meta):
        model = Staff
        fields = CustomStaffForm.Meta.fields

class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Năm học", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']
