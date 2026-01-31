from django.core.management.base import BaseCommand
from tracker.models import Student, Lesson, StudentLessonProgress
from django.utils import timezone


class Command(BaseCommand):
    help = 'Добавить прогресс по урокам для ученика'
    
    def add_arguments(self, parser):
        parser.add_argument('student_id', type=int, help='ID ученика')
        parser.add_argument('lesson_numbers', nargs='+', help='Номера уроков (например: М1У1 М1У2)')
    
    def handle(self, *args, **options):
        student_id = options['student_id']
        lesson_numbers = options['lesson_numbers']
        
        try:
            student = Student.objects.get(id=student_id, is_active=True)
        except Student.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Студент с ID {student_id} не найден"))
            return
        
        added_count = 0
        
        for lesson_number in lesson_numbers:
            try:
                lesson = Lesson.objects.get(full_number=lesson_number)
                
                # Создаем или обновляем прогресс
                progress, created = StudentLessonProgress.objects.get_or_create(
                    student=student,
                    lesson=lesson,
                    defaults={
                        'date_completed': timezone.now().date(),
                        'homework_completed': False
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Добавлен урок {lesson_number} для {student}")
                    )
                    added_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Урок {lesson_number} уже был добавлен для {student}")
                    )
                    
            except Lesson.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Урок {lesson_number} не найден")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Добавлено {added_count} уроков для {student}")
        )