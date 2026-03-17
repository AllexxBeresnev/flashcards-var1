from django.contrib import admin
from django.contrib import messages
from django.urls import path
from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils.html import format_html
import tablib
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from import_export.fields import Field
from .models import Card, Category
from .resources import CardResource, CategoryResource


def reset_group_to_one(modeladmin, request, queryset):
    updated = queryset.update(group=1)
    modeladmin.message_user(
        request,
        f"Группа успешно сброшена до 1 для {updated} карточек.",
        messages.SUCCESS
    )
reset_group_to_one.short_description = "Сбросить группу до 1 (вернуть в обучение)"

def set_group_to_two(modeladmin, request, queryset):
    updated = queryset.update(group=2)
    modeladmin.message_user(request, f"Группа установлена 2 для {updated} карточек.", messages.SUCCESS)
set_group_to_two.short_description = "Установить группу 2"

def set_group_to_three(modeladmin, request, queryset):
    updated = queryset.update(group=3)
    modeladmin.message_user(request, f"Группа установлена 3 для {updated} карточек.", messages.SUCCESS)
set_group_to_three.short_description = "Установить группу 3"

def set_group_to_four(modeladmin, request, queryset):
    updated = queryset.update(group=4)
    modeladmin.message_user(request, f"Группа установлена 4 для {updated} карточек.", messages.SUCCESS)
set_group_to_four.short_description = "Установить группу 4"


class CardImportResource(ModelResource):
    """Ресурс для импорта карточек. Дубликаты слов разрешены."""
    
    class Meta:
        model = Card
        fields = ('word', 'translation', 'category')

    def before_import_row(self, row, **kwargs):
        """Добавляем category к каждой строке перед импортом."""
        category = kwargs.get('category')
        if category:
            row['category'] = category.id


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'words_count', 'import_link')
    search_fields = ('name',)
    fields = ('name',)
    readonly_fields = ('created_at',)

    def import_link(self, obj):
        url = f'/admin/cards/category/{obj.id}/import/'
        return format_html(
            '<a class="button" href="{}">📥 Импорт слов</a>&nbsp;',
            url
        )
    import_link.short_description = 'Импорт'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:category_id>/import/',
                self.admin_site.admin_view(self.import_view),
                name='cards_category_import'
            ),
        ]
        return custom_urls + urls

    def import_view(self, request, category_id):
        category = Category.objects.get(id=category_id)
        
        if request.method == 'POST':
            file = request.FILES.get('file')
            if file:
                try:
                    # Определяем формат по расширению
                    file_ext = file.name.split('.')[-1].lower()

                    # Сопоставляем расширение с форматом
                    format_map = {
                        'xlsx': 'xlsx',
                        'xls': 'xls',
                        'csv': 'csv',
                    }

                    if file_ext not in format_map:
                        messages.error(request, 'Неподдерживаемый формат файла. Используйте XLSX, XLS или CSV.')
                        return redirect('admin:cards_category_changelist')

                    import_format = format_map[file_ext]

                    # Читаем содержимое файла
                    file_content = file.read()
                    
                    # Создаем dataset
                    dataset = tablib.Dataset().load(file_content, format=import_format)
                    
                    # Проверяем что загрузилось
                    if not dataset:
                        messages.error(request, 'Файл пуст или не содержит данных.')
                        return redirect('admin:cards_category_changelist')
                    
                    # Проверяем заголовки
                    if not dataset.headers:
                        messages.error(request, 'Файл не содержит заголовков. Первая строка должна содержать: word, translation1, translation2, translation3')
                        return redirect('admin:cards_category_changelist')
                    
                    # Проверяем наличие данных
                    if len(dataset) == 0:
                        messages.error(request, 'Файл не содержит строк с данными (только заголовки).')
                        return redirect('admin:cards_category_changelist')

                    # Импортируем вручную - создаём карточки напрямую
                    created_count = 0
                    for row in dataset.dict:
                        Card.objects.create(
                            category=category,
                            word=row.get('word', ''),
                            translation=row.get('translation', ''),
                            group=1
                        )
                        created_count += 1

                    if created_count > 0:
                        messages.success(
                            request,
                            f'Импортировано {created_count} слов в тематику "{category.name}"'
                        )
                        return redirect('admin:cards_category_changelist')
                    else:
                        messages.error(request, 'Не удалось импортировать ни одного слова. Проверьте формат файла.')
                        
                except tablib.exceptions.UnsupportedFormat as e:
                    messages.error(request, f'Неподдерживаемый формат файла: {str(e)}')
                    return redirect('admin:cards_category_changelist')
                except Exception as e:
                    messages.error(request, f'Ошибка при обработке файла: {str(e)}')
                    return redirect('admin:cards_category_changelist')
            else:
                messages.error(request, 'Файл не выбран')
        
        context = {
            'category': category,
            'title': f'Импорт слов в тематику "{category.name}"',
        }
        return render(request, 'admin/cards/category/import.html', context)


@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    resource_class = CardResource
    list_display = ('word', 'category', 'group', 'translation')
    list_filter = ('category', 'group')
    search_fields = ('word', 'translation')
    fields = ('category', 'word', 'translation', 'image', 'group')
    actions = [reset_group_to_one, set_group_to_two, set_group_to_three, set_group_to_four]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_site.admin_view(self.statistics_view), name='cards_card_statistics'),
        ]
        return custom_urls + urls

    def statistics_view(self, request):
        stats = Card.objects.values('group').annotate(count=Count('id')).order_by('group')
        total = Card.objects.count()
        context = {
            'stats': stats,
            'total': total,
            'opts': self.model._meta,
        }
        return render(request, 'admin/cards/card/statistics.html', context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_statistics_button'] = True
        return super().changelist_view(request, extra_context=extra_context)