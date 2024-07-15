# content/models.py
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Контент')
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='Изображение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def get_excerpt(self, num_words=200):
        words = self.content.split()[:num_words]
        return ' '.join(words) + '...'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
