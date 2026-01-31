from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg
from .models import Student, Lesson, Homework, Payment, ProgressReport
from .forms import StudentForm, LessonForm, HomeworkForm


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'tracker/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Student.objects.filter(is_active=True)
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(group_number__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'total': Student.objects.count(),
            'active': Student.objects.filter(is_active=True).count(),
            'group': Student.objects.filter(format='group').count(),
            'individual': Student.objects.filter(format='individual').count(),
        }
        return context


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'tracker/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        context['recent_lessons'] = student.lessons.all()[:10]
        context['recent_homeworks'] = student.homeworks.all()[:10]
        context['recent_payments'] = student.payments.all()[:5]
        context['reports'] = student.reports.all()[:5]
        return context


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'tracker/student_form.html'
    success_url = reverse_lazy('student_list')


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'tracker/student_form.html'
    
    def get_success_url(self):
        return reverse_lazy('student_detail', kwargs={'pk': self.object.pk})


class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'tracker/student_form.html'
    
    def form_valid(self, form):
        form.instance.student_id = self.kwargs['student_id']
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('student_detail', 
                          kwargs={'pk': self.kwargs['student_id']})


class HomeworkCreateView(LoginRequiredMixin, CreateView):
    model = Homework
    form_class = HomeworkForm
    template_name = 'tracker/student_form.html'
    
    def form_valid(self, form):
        form.instance.student_id = self.kwargs['student_id']
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('student_detail', 
                          kwargs={'pk': self.kwargs['student_id']})


def dashboard_view(request):
    """Дашборд с общей статистикой"""
    total_students = Student.objects.count()
    active_students = Student.objects.filter(is_active=True).count()
    total_lessons = Lesson.objects.count()
    completed_homeworks = Homework.objects.filter(status='completed').count()
    
    # Статистика по статусам ДЗ
    homework_stats = {
        'green': Student.objects.filter(
            last_homework_lesson__gte=models.F('last_lesson')
        ).count(),
        'yellow': Student.objects.filter(
            last_homework_lesson=models.F('last_lesson') - 1
        ).count(),
        'red': Student.objects.filter(
            last_homework_lesson__lt=models.F('last_lesson') - 1
        ).count(),
    }
    
    # Ближайшие дедлайны по ДЗ
    upcoming_deadlines = Homework.objects.filter(
        deadline__gte=timezone.now().date()
    ).order_by('deadline')[:10]
    
    # Предстоящие платежи
    upcoming_payments = Payment.objects.filter(
        status='pending',
        date__gte=timezone.now().date()
    ).order_by('date')[:10]
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'total_lessons': total_lessons,
        'completed_homeworks': completed_homeworks,
        'homework_stats': homework_stats,
        'upcoming_deadlines': upcoming_deadlines,
        'upcoming_payments': upcoming_payments,
    }
    return render(request, 'tracker/dashboard.html', context)