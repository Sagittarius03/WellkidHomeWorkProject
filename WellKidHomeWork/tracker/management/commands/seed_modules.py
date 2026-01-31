from django.core.management.base import BaseCommand
from tracker.models import Module, Lesson


class Command(BaseCommand):
    help = 'Создание начальных модулей и уроков'
    
    def handle(self, *args, **options):
        # Создаем 8 стандартных модулей
        modules_data = [
            (1, "Основы программирования", 4),
            (2, "ООП и структуры данных", 4),
            (3, "Базы данных и SQL", 4),
            (4, "Веб-разработка", 4),
            (5, "Фреймворки и библиотеки", 4),
            (6, "Тестирование и DevOps", 4),
            (7, "Продвинутые темы", 4),
            (8, "Проектная работа", 4),
        ]
        
        for module_num, name, lessons_count in modules_data:
            module, created = Module.objects.get_or_create(
                number=module_num,
                defaults={
                    'name': name,
                    'total_lessons': lessons_count,
                    'order': module_num
                }
            )
            
            if created:
                # Создаем уроки для модуля
                for i in range(1, lessons_count + 1):
                    Lesson.objects.create(
                        module=module,
                        number_in_module=i,
                        topic=f"Тема {i} модуля {module_num}",
                        description=f"Описание урока {i}",
                        homework_description=f"Домашнее задание к уроку {i}",
                        order=(module_num - 1) * 4 + i
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f"Создан модуль {module_num}: {name}")
                )
        
        # Опционально: создаем дополнительные модули для 12-модульного курса
        extra_modules = [
            (9, "Мобильная разработка", 4),
            (10, "Машинное обучение", 4),
            (11, "Компьютерное зрение", 4),
            (12, "Промышленная разработка", 4),
        ]
        
        for module_num, name, lessons_count in extra_modules:
            Module.objects.get_or_create(
                number=module_num,
                defaults={
                    'name': name,
                    'total_lessons': lessons_count,
                    'order': module_num,
                    'is_active': False  # По умолчанию неактивны
                }
            )
        
        self.stdout.write(
            self.style.SUCCESS("Все модули и уроки успешно созданы!")
        )