from django.db import models
from django.contrib.auth.models import User

class Lesson(models.Model):
    """Модель урока"""
    module = models.PositiveIntegerField(verbose_name='Модуль')
    lesson = models.PositiveIntegerField(verbose_name='Урок')
    
    class Meta:
        ordering = ['module', 'lesson']
        unique_together = ['module', 'lesson']
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
    
    def __str__(self):
        return f'М{self.module}У{self.lesson}'
    
    @property
    def code(self):
        return f'М{self.module}У{self.lesson}'

class Student(models.Model):
    """Модель ученика"""
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    
    GROUP = 'group'
    INDIVIDUAL = 'individual'
    FORMAT_CHOICES = [
        (GROUP, 'Группа'),
        (INDIVIDUAL, 'Индивидуальный'),
    ]
    
    format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default=GROUP,
        verbose_name='Формат обучения'
    )
    group_number = models.CharField(
        max_length=50,
        verbose_name='Номер группы',
        blank=True,
        help_text='Для группового формата'
    )
    
    first_lesson_date = models.DateField(verbose_name='Дата первого урока')
    last_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        related_name='students_last',
        verbose_name='Последний урок'
    )
    last_homework_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students_homework',
        verbose_name='Последний урок с ДЗ'
    )
    
    class Meta:
        ordering = ['last_name', 'first_name']
        
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
    
    def __str__(self):
        return f'{self.last_name} {self.first_name}'
    
    @property
    def full_name(self):
        """Полное имя для отображения в админке"""
        return f'{self.last_name} {self.first_name}'
    
    @property
    def lessons_behind(self):
        """Вычисляет, на сколько уроков отстаёт ученик"""
        if not self.last_lesson or not self.last_homework_lesson:
            return None
        
        # Вычисляем порядковый номер уроков
        last_lesson_num = (self.last_lesson.module - 1) * 100 + self.last_lesson.lesson
        last_hw_lesson_num = (self.last_homework_lesson.module - 1) * 100 + self.last_homework_lesson.lesson
        
        return last_lesson_num - last_hw_lesson_num
    
    def save(self, *args, **kwargs):
        # Очищаем номер группы для индивидуального формата
        if self.format == self.INDIVIDUAL:
            self.group_number = ''
        super().save(*args, **kwargs)