import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WellKidHomeWork.settings')
django.setup()

from tracker.models import Lesson

# Создаем уроки от М1У1 до М5У12
lessons = []
for module in range(1, 13):
    for lesson_num in range(1, 5):
        lessons.append(Lesson(module=module, lesson=lesson_num))

Lesson.objects.bulk_create(lessons)
print(f'Создано {len(lessons)} уроков')