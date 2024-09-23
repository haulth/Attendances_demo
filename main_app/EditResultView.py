from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from .models import Subject, Staff, StudentResult
from .forms import EditResultForm
from django.urls import reverse


class EditResultView(View):
    def get(self, request, *args, **kwargs):
        resultForm = EditResultForm()
        staff = get_object_or_404(Staff, admin=request.user)
        resultForm.fields['subject'].queryset = Subject.objects.filter(staff=staff)
        context = {
            'form': resultForm,
            'page_title': "Chỉnh sửa kết quả học tập của học sinh"
        }
        return render(request, "staff_template/edit_student_result.html", context)

    def post(self, request, *args, **kwargs):
        form = EditResultForm(request.POST)
        context = {'form': form, 'page_title': "Chỉnh sửa kết quả của học sinh"}
        if form.is_valid():
            try:
                student = form.cleaned_data.get('student')
                subject = form.cleaned_data.get('subject')
                test = form.cleaned_data.get('test')
                exam = form.cleaned_data.get('exam')
                # Validating
                result = StudentResult.objects.get(student=student, subject=subject)
                result.exam = exam
                result.test = test
                result.save()
                messages.success(request, "Cập nhật kết quả thành công")
                return redirect(reverse('edit_student_result'))
            except Exception as e:
                messages.warning(request, "Kết quả không thể được cập nhật")
        else:
            messages.warning(request, "Kết quả không thể được cập nhật.")
        return render(request, "staff_template/edit_student_result.html", context)
