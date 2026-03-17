from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, IntegerWidget
from .models import Card, Category

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name', 'created_at')
        export_order = ('id', 'name', 'created_at')

class CardResource(resources.ModelResource):
    class Meta:
        model = Card
        fields = ('id', 'word', 'translation', 'group', 'image', 'category')
        export_order = ('id', 'word', 'translation', 'group', 'image', 'category')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True