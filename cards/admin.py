from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Card
from .resources import CardResource

@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):  # Наследуемся от ImportExportModelAdmin
    resource_class = CardResource
    list_display = ('word', 'group', 'translation1', 'translation2', 'translation3')
    list_filter = ('group',)
    search_fields = ('word', 'translation1', 'translation2', 'translation3')
    fields = ('word', 'translation1', 'translation2', 'translation3', 'image', 'group')