from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@mail.ru',
                                              password='test-pass')
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
        )

        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='rat'
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='Name')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        # Авторизуем пользователя
        self.authorized_author.force_login(self.author)
        self.post.id = 1

    def test_url_exists_at_desired_location(self):
        urls = {
            '/',
            '/group/rat/',
            '/profile/Name/',
            '/posts/1/',
        }
        for address in urls:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_url_for_auth_user(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_url_for_author(self):
        response = self.authorized_author.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/rat/',
            'posts/profile.html': '/profile/Name/',
            'posts/post_detail.html': '/posts/1/',
        }
        for template, address in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_for_auth_user_correct_template(self):
        # страница создания поста авторизованным юзером
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_for_author_correct_template(self):
        # страница создания поста авторизованным автором
        response = self.authorized_author.get('/posts/1/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_page_for_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
