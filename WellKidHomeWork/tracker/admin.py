from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from .models import Student, Lesson

from django.utils.safestring import mark_safe


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['code', 'module', 'lesson']
    list_filter = ['module']
    search_fields = ['module', 'lesson']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    
    class Media:
        css = {
            'all': ('admin/css/hide_links.css',)
        }
    
    
    list_display = [
        'full_name_column', 
        'format_column',
        'last_lesson',
        'last_homework_lesson',
        'lessons_behind_column',
    ]
    
    list_editable = ('last_lesson', 'last_homework_lesson')
    
    # Вариант 1: Убрать ВСЕ ссылки на объекты
    list_display_links = None
    
    # Вариант 2: Если нужно оставить имя как ссылку, но убрать остальное
    # list_display_links = ('full_name_column',)
    
    list_filter = ['format', 'group_number', 'last_lesson__module']
    search_fields = ['first_name', 'last_name', 'email', 'group_number']
    
    # Убираем выпадающее меню действий
    actions = None
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'email', 'first_lesson_date')
        }),
        ('Обучение', {
            'fields': ('format', 'group_number', 'last_lesson', 'last_homework_lesson')
        }),
    )
    
    def full_name_column(self, obj):
        """Отображаем имя и фамилию в одной колонке БЕЗ ссылки"""
        # Если list_display_links = None, то просто возвращаем текст
        return obj.full_name
    
        # ИЛИ если хотите отключить ссылку только для этой колонки:
        # return format_html('<span>{}</span>', obj.full_name)
    
    full_name_column.short_description = 'Имя и Фамилия'
    full_name_column.admin_order_field = 'last_name'
    
    def format_column(self, obj):
        """Отображаем формат с номером группы если есть"""
        if obj.format == Student.GROUP and obj.group_number:
            return f'{obj.get_format_display()} ({obj.group_number})'
        return obj.get_format_display()
    format_column.short_description = 'Формат'
    
    def lessons_behind_column(self, obj):
        """Цветовое оформление отставания"""
        behind = obj.lessons_behind
        if behind is None:
            return '-'
        
        if behind == 0:
            return format_html('<span style="color: green;">✓ Всё сдано</span>', behind)
        elif behind <= 2:
            return format_html('<span style="color: orange;">Отстаёт на {}</span>', behind)
        else:
            return format_html('<span style="color: red; font-weight: bold;">Отстаёт на {}</span>', behind)
    lessons_behind_column.short_description = 'Отставание'
    
    # Опционально: убрать кнопку "Добавить" сверху
    # def has_add_permission(self, request):
    #     return False
    
    # Опционально: убрать возможность удаления
    # def has_delete_permission(self, request, obj=None):
    #     return False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'last_lesson', 'last_homework_lesson'
        )