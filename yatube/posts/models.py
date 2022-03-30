from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True, verbose_name='Идентификатор группы')
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(blank=False, help_text='Текст нового поста',
    verbose_name='Текст поста')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )

    def __str__(self):
        return self.text

    group = models.ForeignKey(
        Group,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        help_text='Группа, '
                  'к которой относится пост',
        verbose_name='Группа'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Записи блогов'
