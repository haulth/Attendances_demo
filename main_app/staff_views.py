import json, pytz
import logging
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .forms import *
from .models import *
from django.db.models import Count, Case, When, IntegerField
from datetime import date
from collections import defaultdict


def staff_home(request):
    # Lấy thông tin giáo viên hiện tại
    staff = get_object_or_404(Staff, admin=request.user)
    today = timezone.now().date()

    # Lấy lịch giảng dạy của giáo viên cho ngày hôm nay
    teaching_schedules_today = TeachingSchedule.objects.filter(
        staff=staff, schedule_date=today
    )

    # Lấy tổng số lớp và tên lớp mà giáo viên dạy hôm nay
    total_subject = teaching_schedules_today.count()
    class_names = teaching_schedules_today.values_list("class_name__name", flat=True)

    # Lấy số học sinh theo từng lớp
    class_students_count = (
        Student.objects.filter(
            session__in=teaching_schedules_today.values_list("class_name", flat=True)
        )
        .values("session__name")
        .annotate(total_students=Count("id"))
    )

    # Chuyển kết quả thành dict với tên lớp và số lượng học sinh
    class_students_data = {
        class_data["session__name"]: class_data["total_students"]
        for class_data in class_students_count
    }

    # Đảm bảo tất cả các lớp đều có trong dict, kể cả khi không có học sinh
    for class_name in class_names:
        if class_name not in class_students_data:
            class_students_data[class_name] = 0
            
    for schedule in teaching_schedules_today:
        subject_id = schedule.class_name.id  # Lấy subject_id từ class_name
        session_id = schedule.school_name.id  # Lấy session_id từ school_name
        date = schedule.schedule_date

        try:
            # Tìm Attendance đã tồn tại cho môn học và lớp học theo ngày
            attendance = Attendance.objects.get(
                subject_id=subject_id, session_id=session_id, date=date
            )

            # Tìm danh sách học sinh theo môn học (subject) và lớp học (session)
            students = Student.objects.filter(session_id=subject_id)
            print(f"Tìm thấy {students.count()} học sinh trong môn học {subject_id}")

           
            for student in students:
                report_exists = AttendanceReport.objects.filter(
                    student=student,
                    attendance=attendance,
                ).exists()

                if not report_exists:
                    # Tạo mới AttendanceReport cho học sinh nếu chưa tồn tại
                    AttendanceReport.objects.create(
                        student=student,
                        attendance=attendance,
                        status=False,  # Mặc định là chưa điểm danh
                    )
            print("Lưu trạng thái chưa điểm danh cho tất cả học sinh chưa được điểm danh")

        except Attendance.DoesNotExist:
            print(f"Attendance không tồn tại cho môn {subject_id} và lớp {session_id}")
       
    # Lấy danh sách học sinh có điểm danh và vắng mặt cho hôm nay
    students = Student.objects.filter(
        session__in=teaching_schedules_today.values_list("class_name", flat=True)
    ).annotate(
        present_count=Count(
            Case(
                When(
                    attendancereport__status=True,
                    attendancereport__attendance__date=today,
                    then=1,
                ),
                output_field=IntegerField(),
            )
        ),
        leave_count=Count(
            Case(
                When(
                    attendancereport__status=False,
                    attendancereport__attendance__date=today,
                    then=1,
                ),
                output_field=IntegerField(),
            )
        ) + Count(
            Case(
                When(
                    leavereportstudent__status=1, 
                    leavereportstudent__date=today, 
                    then=1
                ),
                output_field=IntegerField(),
            )
        ),
    )

    # Lấy danh sách học sinh chưa điểm danh
    students_not_reported = Student.objects.filter(
        session__in=teaching_schedules_today.values_list("class_name", flat=True)
    ).exclude(id__in=students.values_list("id", flat=True))

    # Tạo dict để nhóm học sinh theo trường và tính số lượng có mặt, vắng mặt
    school_attendance = defaultdict(
        lambda: {"present_count": 0, "leave_count": 0, "not_reported_count": 0}
    )

    for student in students.distinct():
        teaching_schedule = teaching_schedules_today.filter(
            class_name=student.session
        ).first()
        school_name = teaching_schedule.school_name.name if teaching_schedule else "N/A"

        school_attendance[school_name]["present_count"] += student.present_count
        school_attendance[school_name]["leave_count"] += student.leave_count

    # Đếm số lượng học sinh chưa điểm danh theo trường
    for student in students_not_reported:
        teaching_schedule = teaching_schedules_today.filter(
            class_name=student.session
        ).first()
        school_name = teaching_schedule.school_name.name if teaching_schedule else "N/A"

        # school_attendance[school_name]["not_reported_count"] += 1

    # Tạo context để truyền vào template
    context = {
        "page_title": "Bảng quản lý - "
        + str(staff.admin.last_name)
        + " "
        + str(staff.admin.first_name),
        "class_students_data": class_students_data,
        "school_attendance": dict(school_attendance),
        "teaching_schedules_today": teaching_schedules_today,
        "total_subject": total_subject,
        "class_names": class_names,
    }
    print(context)
    return render(request, "staff_template/home_content.html", context)



def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    
     # Lấy thời gian hiện tại
    current_date = timezone.now().date()
    # Kiểm tra xem giáo viên có lịch dạy vào ngày hiện tại hay không
    has_schedule_today = TeachingSchedule.objects.filter(staff=staff, schedule_date=current_date).exists()

    # Nếu giáo viên không có lịch dạy hôm nay, chặn truy cập và thông báo
    if not has_schedule_today:
        messages.error(request, "Bạn không có lịch dạy hôm nay!")
        return redirect("staff_home")
    teachingSchedule = TeachingSchedule.objects.filter(staff_id=staff)

    # Lấy danh sách các lớp (subject) và các trường (session)
    subjects = [schedule.list_class_name() for schedule in teachingSchedule]

    # Sử dụng set() để loại bỏ các trường trùng lặp
    sessions = list(set(schedule.list_school_name() for schedule in teachingSchedule))

    context = {
        "subjects": subjects,
        "sessions": sessions,  # Danh sách các trường không trùng lặp
        "page_title": "Điểm danh",
    }

    return render(request, "staff_template/staff_take_attendance.html", context)


def get_subjects_by_session_staff(request):
    session_id = request.GET.get("session_id")
    subjects = Subject.objects.filter(course_id=session_id)  # Lọc lớp theo trường
    subject_list = [{"id": subject.id, "name": subject.name} for subject in subjects]

    return JsonResponse({"subjects": subject_list})


@csrf_exempt
def qr_code_scanner(request):
    if request.method == "POST":
        print('NHẬN DỮ LIỆU')
        subject_id = request.POST.get('subject_id')
        session_id = request.POST.get('session_id')
        date = request.POST.get('date')
        
        # Lấy danh sách học sinh theo lớp (subject_id)
        students = Student.objects.filter(session_id=subject_id)
        print(f'học sinh: {students}')

        # Kiểm tra hoặc tạo Attendance cho buổi học này
        attendance, created = Attendance.objects.get_or_create(
                subject_id=subject_id,
                session_id=session_id,
                date=date
            )

        # Thêm tất cả các báo cáo điểm danh với trạng thái False cho học sinh
        for student in students:
                AttendanceReport.objects.get_or_create(
                    student=student,
                    attendance=attendance,
                    defaults={'status': False}
                )
                
        qr_data = request.POST.get('qr_code_data')
        print(qr_data)
        if not qr_data:
            return JsonResponse({"status": "failed", "message": "Không nhận được dữ liệu mã QR!"})

        try:
            # Tìm học sinh theo mã học sinh (qr_data)
            student = get_object_or_404(Student, admin__student_id=qr_data)
            print(f"Học sinh tìm thấy: {student.admin.first_name} {student.admin.last_name}")

            # Kiểm tra hoặc tạo Attendance
            attendance, created = Attendance.objects.get_or_create(
                subject_id=request.POST.get('subject_id'),
                session_id=request.POST.get('session_id'),
                date=request.POST.get('date')
            )
            if created:
                print("Tạo mới Attendance")
            else:
                print("Tìm thấy Attendance hiện có")

            # Kiểm tra xem học sinh này đã có AttendanceReport hay chưa
            attendance_report = AttendanceReport.objects.filter(student=student, attendance=attendance).first()
            

            # Kiểm tra trạng thái của học sinh đã điểm danh hay chưa
            if attendance_report.status:
                # Nếu sinh viên đã được điểm danh, trả về thông báo
                print("Học sinh này đã được điểm danh trước đó.")
                return JsonResponse({
                    "status": "failed",
                    "message": "Học sinh này đã được điểm danh trước đó!"
                })
            else:
                # Nếu trạng thái là False, cập nhật lại điểm danh
                attendance_report.status = True
                attendance_report.save()
                print("Cập nhật điểm danh thành công!")

            # Lấy thông tin thời gian hiện tại theo múi giờ Việt Nam
            vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            timestamp = timezone.now().astimezone(vn_tz).strftime('%d-%m-%Y %H:%M:%S')

            # Trả về thông tin học sinh và thời gian điểm danh
            return JsonResponse({
                "status": "success",
                "message": "Điểm danh thành công!",
                "student_id": student.admin.student_id,
                "student_name": f"{student.admin.last_name} {student.admin.first_name} ",
                "timestamp": timestamp
            })

        except Student.DoesNotExist:
            return JsonResponse({"status": "failed", "message": "Không tìm thấy học sinh!"})
        except Attendance.DoesNotExist:
            return JsonResponse({"status": "failed", "message": "Không tìm thấy thông tin điểm danh!"})
        except Exception as e:
            print(f"Lỗi: {e}")
            return JsonResponse({"status": "failed", "message": f"Có lỗi xảy ra: {str(e)}"})

    return JsonResponse({"status": "failed", "message": "Yêu cầu không hợp lệ!"})



logger = logging.getLogger(__name__)
@csrf_exempt
def get_students(request):
    subject_name = request.POST.get("subject")  # Lấy tên lớp từ request
    school_name = request.POST.get("session")  # Lấy tên trường từ request

    try:
        # Lấy Course (School) dựa trên id
        course = get_object_or_404(Course, id=school_name)

        if subject_name:
            # Nếu có subject_id, lấy Subject dựa trên id
            subject = get_object_or_404(Subject, id=subject_name)
            # Lọc danh sách học sinh theo course và subject
            students = Student.objects.filter(course=course, session=subject)
        else:
            # Nếu không có subject_id, chỉ lọc theo course
            students = Student.objects.filter(course=course)

        # Kiểm tra nếu không có học sinh nào
        if not students.exists():
            return JsonResponse(
                {"message": "Không có học sinh nào được tìm thấy"}, status=404
            )

        # Tạo danh sách học sinh dưới dạng JSON
        student_data = [
            {
                "id": student.id,
                "name": student.admin.last_name + " " + student.admin.first_name,
            }
            for student in students
        ]
        print(student_data)
        return JsonResponse(student_data, safe=False, status=200)

    except Exception as e:
        logger.error(f"Lỗi xảy ra: {str(e)}")
        return JsonResponse({"error": "Lỗi máy chủ. Vui lòng thử lại sau."}, status=500)


@csrf_exempt
def save_attendance(request):
    try:
        student_data = request.POST.get("student_ids")
        date = request.POST.get("date")
        subject_id = request.POST.get("subject")
        session_id = request.POST.get("session")

        # Log lại các giá trị nhận được
        logger.info(
            f"Nhận được dữ liệu: student_data={student_data}, date={date}, subject_id={subject_id}, session_id={session_id}"
        )

        students = json.loads(student_data)

        # Lấy session và subject từ id
        session = get_object_or_404(Course, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)

        # Kiểm tra xem đã có bản ghi điểm danh cho ngày, lớp và môn học này chưa
        attendance, created = Attendance.objects.get_or_create(
            session=session, subject=subject, date=date
        )

        if not created:
            # Nếu bản ghi đã tồn tại, xóa tất cả các báo cáo điểm danh cũ
            AttendanceReport.objects.filter(attendance=attendance).delete()

        # Lưu bản ghi cho từng học sinh
        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get("id"))
            attendance_report = AttendanceReport(
                student=student,
                attendance=attendance,
                status=student_dict.get("status"),
            )
            attendance_report.save()

        return HttpResponse("OK")

    except Exception as e:
        logger.error(f"Lỗi xảy ra khi lưu điểm danh: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


def staff_update_attendance(request):
    try:
        # lấy id nhân viên
        staff = get_object_or_404(Staff, admin=request.user)

        teaching_schedules = TeachingSchedule.objects.filter(staff=staff)

        # láy tên lớp dựa trên lịch dạy của gióa viên
        subjects = Subject.objects.filter(
            id__in=teaching_schedules.values_list("class_name", flat=True).distinct()
        )

        # láy tên trường dựa trên lịch dạy của gióa viên
        sessions = Course.objects.filter(
            id__in=teaching_schedules.values_list("school_name", flat=True).distinct()
        )

        context = {
            "subjects": subjects,
            "sessions": sessions,
            "page_title": "Xem điểm danh",
        }

        return render(request, "staff_template/staff_update_attendance.html", context)

    except Exception as e:
        logger.error(f"Lỗi khi cập nhật điểm danh: {str(e)}")
        return HttpResponse("Lỗi máy chủ. Vui lòng thử lại sau.", status=500)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get("attendance_date_id")
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {
                "id": attendance.student.admin.id,
                "name": attendance.student.admin.last_name
                + " "
                + attendance.student.admin.first_name,
                "status": attendance.status,
            }
            student_data.append(data)
        return JsonResponse(
            json.dumps(student_data), content_type="application/json", safe=False
        )
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get("student_ids")
    date = request.POST.get("date")
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, student_id=student_dict.get("student_id")
            )  # Sửa từ admin_id sang student_id
            attendance_report = get_object_or_404(
                AttendanceReport, student=student, attendance=attendance
            )
            attendance_report.status = student_dict.get("status")
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = TeachingSchedule(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)

    # Lấy danh sách các buổi dạy của nhân viên
    sessions = TeachingSchedule.objects.filter(staff=staff)

    # Lấy danh sách các buổi dạy đã hoàn thành của nhân viên
    completed_sessions = CompletedTeachingSchedule.objects.filter(staff_id=staff.admin)
    completed_session_ids = completed_sessions.values_list("schedule_id", flat=True)
    today = date.today()

    context = {
        "today": today,
        "form": form,
        "sessions": sessions,
        "completed_session_ids": completed_session_ids,
        "page_title": "Lịch dạy",
    }

    return render(request, "staff_template/staff_apply_leave.html", context)


def complete_teaching_schedule(request):
    if request.method == "POST":
        session_ids = request.POST.getlist("session_id[]")
        print("Dữ liệu nhận được:", session_ids)  # Kiểm tra dữ liệu đầu vào

        if not session_ids:
            messages.warning(request, "Bạn chưa chọn buổi dạy nào để hoàn thành.")
            return redirect("staff_apply_leave")

        for session_id in session_ids:
            try:
                session = TeachingSchedule.objects.get(id=session_id)

                # Giả sử session.staff là một đối tượng Staff và có thuộc tính `user` liên kết đến CustomUser
                custom_user = session.staff.admin  # Truy cập đến đối tượng CustomUser

                # Kiểm tra xem buổi dạy đã được lưu trong CompletedTeachingSchedule chưa
                if not CompletedTeachingSchedule.objects.filter(
                    schedule=session
                ).exists():
                    CompletedTeachingSchedule.objects.create(
                        staff=custom_user,  # Gán đối tượng CustomUser
                        schedule=session,
                        completed_date=session.schedule_date,
                    )
            except TeachingSchedule.DoesNotExist:
                messages.error(request, f"Buổi dạy ID {session_id} không tồn tại.")
                continue

        messages.success(request, "Cập nhật hoàn tất.")
        return redirect("staff_apply_leave")


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        "form": form,
        "feedbacks": FeedbackStaff.objects.filter(staff=staff),
        "page_title": "Thêm phản hồi",
    }
    if request.method == "POST":
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Phản hồi đã được gửi để xem xét")
                return redirect(reverse("staff_feedback"))
            except Exception:
                messages.error(request, "Không thể gửi!")
        else:
            messages.error(request, "Mẫu đơn có lỗi!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    # Lấy thông tin nhân viên hiện tại dựa trên user đã đăng nhập
    staff = get_object_or_404(Staff, admin=request.user)

    # Tạo form với thông tin hiện tại của nhân viên
    form = StaffEditForm(
        request.POST or None, request.FILES or None, instance=staff, user_type="staff"
    )

    context = {"form": form, "page_title": "Cập nhật thông tin", "user_type": "staff"}

    if request.method == "POST":
        try:
            if form.is_valid():
                # Lấy dữ liệu từ form
                first_name = form.cleaned_data.get("first_name")
                last_name = form.cleaned_data.get("last_name")
                password = form.cleaned_data.get("password") or None
                address = form.cleaned_data.get("address")
                gender = form.cleaned_data.get("gender")
                passport = request.FILES.get("profile_pic") or None

                admin = staff.admin

                # Cập nhật mật khẩu nếu có
                if password:
                    admin.set_password(password)

                # Cập nhật hình đại diện nếu có
                if passport:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url

                # Cập nhật các thông tin khác
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                staff.save()

                messages.success(request, "Thông tin được cập nhật!")
                return redirect(reverse("staff_view_profile"))
            else:
                messages.error(request, "Dữ liệu cung cấp không hợp lệ.")
        except Exception as e:
            messages.error(request, "Đã xảy ra lỗi khi cập nhật hồ sơ. " + str(e))

    # Trả về trang cập nhật thông tin với form đã được load sẵn thông tin hiện tại
    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get("token")
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    # Lấy thông tin giáo viên hiện tại
    staff = get_object_or_404(Staff, admin=request.user)

    # Lấy thời gian hiện tại
    current_date = timezone.now().date()

    # Kiểm tra xem giáo viên có lịch dạy vào ngày hiện tại hay không
    has_schedule_today = TeachingSchedule.objects.filter(staff=staff, schedule_date=current_date).exists()

    # Nếu giáo viên không có lịch dạy hôm nay, chặn truy cập và thông báo
    if not has_schedule_today:
        messages.error(request, "Bạn không có lịch dạy hôm nay!")
        return redirect("staff_home")

    # Lấy danh sách lịch dạy của giáo viên
    teachingSchedule = TeachingSchedule.objects.filter(staff_id=staff)

    # Sử dụng set để loại bỏ các lớp học và trường học bị trùng lặp
    class_names = {schedule.list_class_name() for schedule in teachingSchedule}
    school_names = {schedule.list_school_name() for schedule in teachingSchedule}

    sessions = Course.objects.all()

    # Truyền thông tin vào context để hiển thị trên trang
    context = {
        "subjects": list(class_names),  # Chuyển set về list để có thể sử dụng trong template
        "sessions": list(school_names),  # Chuyển set về list
        "page_title": "Điểm danh với mã QR",
    }

    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff=staff)
    sessions = Session.objects.all()
    context = {
        "page_title": "Cập nhật kết quả",
        "subjects": subjects,
        "sessions": sessions,
    }
    if request.method == "POST":
        try:
            student_id = request.POST.get("student_list")
            subject_id = request.POST.get("subject")
            test = request.POST.get("test")
            exam = request.POST.get("exam")
            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            try:
                data = StudentResult.objects.get(student=student, subject=subject)
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Điểm số đã được cập nhật")
            except:
                result = StudentResult(
                    student=student, subject=subject, test=test, exam=exam
                )
                result.save()
                messages.success(request, "Đã lưu điểm số")
        except Exception as e:
            messages.warning(request, "Đã xảy ra lỗi khi xử lý mẫu đơn.")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    try:
        subject_id = request.POST.get("subject")
        student_id = request.POST.get("student")
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        result = StudentResult.objects.get(student=student, subject=subject)
        result_data = {"exam": result.exam, "test": result.test}
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse("False")
