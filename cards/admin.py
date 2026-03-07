from django.contrib import admin
from django.contrib import messages
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from import_export.admin import ImportExportModelAdmin
from .models import Card
from .resources import CardResource

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

@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    resource_class = CardResource
    list_display = ('word', 'group', 'translation1', 'translation2', 'translation3')
    list_filter = ('group',)
    search_fields = ('word', 'translation1', 'translation2', 'translation3')
    fields = ('word', 'translation1', 'translation2', 'translation3', 'image', 'group')
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