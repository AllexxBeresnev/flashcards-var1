from django.contrib import admin
from .models import Card

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('word', 'group', 'translation1', 'translation2', 'translation3')
    list_filter = ('group',)
    search_fields = ('word', 'translation1', 'translation2', 'translation3')
    fields = ('word', 'translation1', 'translation2', 'translation3', 'image', 'group')