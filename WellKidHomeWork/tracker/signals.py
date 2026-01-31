from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import StudentLessonProgress, Student


@receiver([post_save, post_delete], sender=StudentLessonProgress)
def update_student_progress(sender, instance, **kwargs):
    """
    Автоматически обновляет прогресс студента при изменении прогресса по урокам
    """
    student = instance.student
    
    # Находим последний пройденный урок
    last_progress = StudentLessonProgress.objects.filter(
        student=student
    ).order_by('-lesson__order').first()
    
    if last_progress:
        student.last_lesson = last_progress.lesson
    else:
        student.last_lesson = None
    
    # Находим последний урок с выполненным ДЗ
    last_homework = StudentLessonProgress.objects.filter(
        student=student,
        homework_completed=True
    ).order_by('-lesson__order').first()
    
    if last_homework:
        student.last_homework_lesson = last_homework.lesson
    else:
        student.last_homework_lesson = None
    
    student.save(update_fields=['last_lesson', 'last_homework_lesson'])