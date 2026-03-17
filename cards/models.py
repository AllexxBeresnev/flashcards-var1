from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField("Название тематики", max_length=200, unique=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Тематика"
        verbose_name_plural = "Тематики"
        ordering = ['name']

    def __str__(self):
        return self.name

    def words_count(self):
        """Подсчет количества слов в тематике (группа 1)."""
        return self.cards.filter(group=1).count()
    words_count.short_description = "Количество слов"


class Card(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='cards',
        verbose_name="Тематика",
        null=True,
        blank=True
    )
    word = models.CharField("Слово на языке оригинала", max_length=200)
    translation = models.CharField("Перевод", max_length=200, default='')
    image = models.ImageField("Изображение", upload_to='cards/', blank=True, null=True)
    group = models.PositiveSmallIntegerField(
        "Группа",
        default=1,
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4")]
    )

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"

    def __str__(self):
        return self.word