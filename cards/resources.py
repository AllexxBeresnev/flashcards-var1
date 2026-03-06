from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, IntegerWidget
from .models import Card

class CardResource(resources.ModelResource):
    # Можно явно определить поля, если нужна кастомная обработка
    class Meta:
        model = Card
        fields = ('id', 'word', 'translation1', 'translation2', 'translation3', 'group', 'image')
        export_order = ('id', 'word', 'translation1', 'translation2', 'translation3', 'group', 'image')
        import_id_fields = ('id',)  # Позволяет обновлять существующие записи по ID
        skip_unchanged = True  # Пропускать неизмененные записи при импорте
        report_skipped = True  # Сообщать о пропущенных записях