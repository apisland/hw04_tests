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
        """Тест help_text в модели Post"""
        post = PostModelTest.post
        help_texts = post._meta.get_field('text').help_text
        self.assertEqual(help_texts, 'Текст нового поста')

    def test_post_models_group_help_text(self):
        """Тест help_text group в модели Post"""
        post = PostModelTest.post
        help_texts = post._meta.get_field('group').help_text
        self.assertEqual(help_texts, 'Группа, '
                  'к которой относится пост')

    def test_post_model_text_verbose(self):
        """Тест поля text verbose"""
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст поста')

    def test_post_model_pubdate_verbose(self):
        """Тест поля pub_date verbose"""
        post = PostModelTest.post
        verbose = post._meta.get_field('pub_date').verbose_name
        self.assertEqual(verbose, 'Дата публикации')

    def test_post_model_author_verbose(self):
        """Тест поля author verbose"""
        post = PostModelTest.post
        verbose = post._meta.get_field('author').verbose_name
        self.assertEqual(verbose, 'Автор')

    def test_post_model_group_verbose(self):
        """Тест поля group verbose"""
        post = PostModelTest.post
        verbose = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose, 'Группа')

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
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Название группы')

    def test_group_model_slug_verbose(self):
        """Тест поля slug verbose"""
        group = GroupModelTest.group
        verbose = group._meta.get_field('slug').verbose_name
        self.assertEqual(verbose, 'Идентификатор группы')

    def test_group_model_description_verbose(self):
        """Тест поля description verbose"""
        group = GroupModelTest.group
        verbose = group._meta.get_field('description').verbose_name
        self.assertEqual(verbose, 'Описание группы')
