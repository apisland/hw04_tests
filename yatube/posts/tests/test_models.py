from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        value = post.text[:settings.POST_MOD]
        self.assertEqual(value, str(post))

    def test_post_models_help_text(self):
        """Тест help_texts в модели Post"""
        post = PostModelTest.post
        values = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой относится пост',
        }
        for key, value in values.items():
            with self.subTest(value=value):
                help_texts = post._meta.get_field(key).help_text
        self.assertEqual(help_texts, value)

    def test_post_model_verbose(self):
        """Тест полей verbose в модели Post"""
        post = PostModelTest.post
        values = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for key, value in values.items():
            with self.subTest(value=value):
                verbose = post._meta.get_field(key).verbose_name
        self.assertEqual(verbose, value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_models_have_correct_object_names(self):
        """Проверяем, что у моделей группы корректно работает __str__."""
        group = GroupModelTest.group
        value = group.title
        self.assertEqual(value, str(group))

    def test_group_model_title_verbose(self):
        """Тест поля title verbose"""
        group = GroupModelTest.group
        values = {
            'title': 'Название группы',
            'slug': 'Идентификатор группы',
            'description': 'Описание группы',
        }
        for key, value in values.items():
            with self.subTest(value=value):
                verbose = group._meta.get_field(key).verbose_name
        self.assertEqual(verbose, value)
