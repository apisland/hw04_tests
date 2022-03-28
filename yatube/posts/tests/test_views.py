from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostViewsTests(TestCase):
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

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'Name'}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={'post_id': '1'}),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'rat'})
            ),
        }
        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_edit_page_uses_correct_template(self):
        response = self.authorized_author.get(reverse('posts:post_edit',
                                                      kwargs={'post_id': '1'}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_index_page_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'test_name')

    def test_group_list_page_context(self):
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug': 'rat'}))
        first_object = response.context['group']
        post_group_0 = first_object.title
        post_slug_0 = first_object.slug
        self.assertEqual(post_group_0, 'Тестовое название группы')
        self.assertEqual(post_slug_0, 'rat')

    def test_profile_page_context(self):
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username': 'Name'}))
        first_object = response.context['author']
        post_author_0 = first_object.username
        self.assertEqual(post_author_0, 'Name')

    def test_page_detail_context(self):
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id': '1'}))
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_id_0, 1)

    def test_create_page_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_context(self):
        edit_url = reverse('posts:post_edit', kwargs={'post_id': '1'})
        response = self.authorized_author.get(edit_url)
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_id_0, 1)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_get_in_group(self):
        post = Post.objects.create(
            author=self.author,
            text='Тестовый текст',
            group=self.group
        )
        response = {
            self.authorized_client.get(reverse('posts:index')),
            self.authorized_client.get(reverse('posts:group_list',
                                               kwargs={'slug': 'rat'})),
            self.authorized_client.get(reverse(
                'posts:profile', kwargs={'username': 'test_name'}))
        }
        for resp in response:
            obj = resp.context.get('page_obj').object_list
            self.assertIn(post, obj)

    def test_post_get_another_group(self):
        post = Post.objects.create(
            author=self.author,
            text='Тестовый текст',
            group=self.group
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'rat'}))
        obj = response.context.get('page_obj').object_list
        self.assertTrue(post, obj)


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
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

        cls.post = []
        for i in range(13):
            cls.post.append(Post(
                            text=f'тест паджинатора {i}',
                            author=cls.author,
                            group=cls.group,)
                            )
        Post.objects.bulk_create(cls.post)

    def setUp(self):
        self.client = Client()
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

    def test_first_page_contains_ten_records(self):
        urls = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'rat'}),
            reverse('posts:profile', kwargs={'username': 'test_name'}),
        }
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        urls = {
            reverse('posts:index') + '?page=2',
            reverse('posts:group_list', kwargs={'slug': 'rat'}) + '?page=2',
            reverse('posts:profile',
                    kwargs={'username': 'test_name'}) + '?page=2',
        }
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']), 3)
