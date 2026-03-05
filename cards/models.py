from django.db import models

class Card(models.Model):
    word = models.CharField("Слово на языке оригинала", max_length=200)
    translation1 = models.CharField("Перевод 1", max_length=200)
    translation2 = models.CharField("Перевод 2", max_length=200, blank=True, null=True)
    translation3 = models.CharField("Перевод 3", max_length=200, blank=True, null=True)
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

    def get_translations(self):
        """Возвращает список непустых переводов карточки."""
        translations = [self.translation1]
        if self.translation2:
            translations.append(self.translation2)
        if self.translation3:
            translations.append(self.translation3)
        return translations