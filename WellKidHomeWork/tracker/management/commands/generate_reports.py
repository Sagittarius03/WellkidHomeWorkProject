from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tracker.models import Student, AutomatedReport


class Command(BaseCommand):
    help = 'Автоматическая генерация отчетов об успеваемости'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            choices=['week', 'month', 'quarter'],
            default='month',
            help='Период для отчета (week/month/quarter)'
        )
        parser.add_argument(
            '--all-students',
            action='store_true',
            help='Генерировать отчеты для всех активных учеников'
        )
    
    def handle(self, *args, **options):
        period = options['period']
        all_students = options.get('all_students')
        
        # Определяем даты периода
        end_date = timezone.now().date()
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        else:  # quarter
            start_date = end_date - timedelta(days=90)
        
        if all_students:
            students = Student.objects.filter(is_active=True)
            self.stdout.write(f"Генерация отчетов для {students.count()} учеников...")
        else:
            # Если не указан --all-students, запрашиваем ID студента
            student_id = input("Введите ID ученика (или нажмите Enter для всех): ").strip()
            
            if student_id:
                try:
                    students = Student.objects.filter(id=int(student_id), is_active=True)
                    if not students.exists():
                        self.stdout.write(self.style.ERROR(f"Студент с ID {student_id} не найден или неактивен"))
                        return
                except ValueError:
                    self.stdout.write(self.style.ERROR("Некорректный ID студента"))
                    return
            else:
                students = Student.objects.filter(is_active=True)
        
        reports_created = 0
        
        for student in students:
            # Проверяем, есть ли прогресс за период
            has_progress = student.studentlessonprogress_set.filter(
                date_completed__range=[start_date, end_date]
            ).exists()
            
            if not has_progress:
                self.stdout.write(
                    self.style.WARNING(
                        f"Нет данных для студента {student} за период {start_date} - {end_date}"
                    )
                )
                continue
            
            # Создаем отчет
            report = AutomatedReport.objects.create(
                student=student,
                period_start=start_date,
                period_end=end_date,
            )
            
            # Генерируем данные отчета
            if report.generate_report():
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Создан отчет для {student} за {start_date} - {end_date}"
                    )
                )
                reports_created += 1
            else:
                report.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно создано {reports_created} отчетов"
            )
        )