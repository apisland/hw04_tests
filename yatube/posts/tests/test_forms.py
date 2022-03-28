from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group
from posts.forms import PostForm


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@mail.ru',
                                              password='test-pass')

        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='rat'
        )

        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group
        )

        cls.form = PostForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='Name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.post.id = 1

    def test_post_create_form(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст в форме',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'Name'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                text='Текст в форме',
                group=self.group.id,
            ).exists()
        )

    def test_post_edit_with_post_id(self):
        self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group.id,
            'post_id': self.post.id
        }

        url = reverse('posts:post_edit', kwargs={'post_id': '1'})
        self.authorized_author.post(
            url,
            data=form_data,
            follow=True
        )

        self.assertTrue(
            Post.objects.filter(
                text='Новый текст в форме',
                group=self.group.id,
                id=self.post.id
            ).exists()
        )
