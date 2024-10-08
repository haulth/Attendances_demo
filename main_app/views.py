import json
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
from .models import Attendance, Subject, Course, AttendanceReport

# Create your views here.


def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == "1":
            return redirect(reverse("admin_home"))
        elif request.user.user_type == "2":
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))
    return render(request, "main_app/login.html")


def doLogin(request, **kwargs):
    if request.method != "POST":
        return HttpResponse("<h4>Denied</h4>")
    else:
        # Bỏ qua phần kiểm tra reCAPTCHA
        # captcha_token = request.POST.get("g-recaptcha-response")
        # captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        # captcha_key = "6LfswtgZAAAAABX9gbLqe-d97qE2g1JP8oUYritJ"
        # data = {"secret": captcha_key, "response": captcha_token}
        # try:
        #     captcha_server = requests.post(url=captcha_url, data=data)
        #     response = json.loads(captcha_server.text)
        #     if response["success"] == False:
        #         messages.error(request, "Captcha không hợp lệ. Vui lòng thử lại.")
        #         return redirect("/")
        # except:
        #     messages.error(request, "Captcha không thể xác thực. Vui lòng thử lại.")
        #     return redirect("/")

        # Authenticate
        user = EmailBackend.authenticate(
            request,
            username=request.POST.get("email"),
            password=request.POST.get("password"),
        )
        if user != None:
            login(request, user)
            if user.user_type == "1":
                return redirect(reverse("admin_home"))
            elif user.user_type == "2":
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            messages.error(request, "Thông tin không hợp lệ")
            return redirect("/")



def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


# @csrf_exempt
# def get_attendance(request):
#     subject_id = request.POST.get("subject") #lớp
#     session_id = request.POST.get("session") #trường
#     try:
#         subject = get_object_or_404(Subject, id=subject_id)
#         session = get_object_or_404(Course, id=session_id)
#         attendance = Attendance.objects.filter(subject=subject, session=session)
#         attendance_list = []
#         for attd in attendance:
#             data = {
#                 "id": attd.id,
#                 "attendance_date": str(attd.date),
#                 "session": attd.session.id,
#             }
#             attendance_list.append(data)
#         return JsonResponse(json.dumps(attendance_list), safe=False)
#     except Exception as e:
#         return None
 
@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get("subject")  # lớp
    session_id = request.POST.get("session")  # trường
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Course, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)

        attendance_list = []
        for attd in attendance:
            # Kiểm tra nếu có học sinh điểm danh 
            has_students = AttendanceReport.objects.filter(attendance=attd).exists()

            if has_students:
                # Chỉ giữ lại những ngày có học sinh điểm danh
                data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id,
                }
                attendance_list.append(data)
            else:
                # Xóa bản ghi Attendance không có học sinh điểm danh
                attd.delete()

        return JsonResponse(json.dumps(attendance_list), safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

