from django import forms
from .models import Student, Lesson, Homework, Payment, ProgressReport
from django.core.exceptions import ValidationError


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'first_lesson_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        last_lesson = cleaned_data.get('last_lesson')
        last_homework_lesson = cleaned_data.get('last_homework_lesson')
        
        if last_homework_lesson > last_lesson:
            raise ValidationError(
                "Номер урока по ДЗ не может быть больше номера последнего урока"
            )
        return cleaned_data


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['lesson_number', 'date', 'topic', 'duration', 
                 'notes', 'materials_used', 'is_completed']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'materials_used': forms.Textarea(attrs={'rows': 3}),
            'duration': forms.TextInput(attrs={'placeholder': 'HH:MM:SS'}),
        }


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['lesson_number', 'status', 'description', 
                 'student_work', 'teacher_feedback', 'grade', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'student_work': forms.Textarea(attrs={'rows': 3}),
            'teacher_feedback': forms.Textarea(attrs={'rows': 3}),
        }