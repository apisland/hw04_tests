from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings

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
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username':
                                                  f'{self.user.username}'}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      f'{self.post.id}'}),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug':
                                                    f'{self.group.slug}'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_edit_page_uses_correct_template(self):
        """Страница редактирования использует корректный шаблон"""
        response = self.authorized_author.get(reverse('posts:post_edit',
                                                      kwargs={'post_id':
                                                              f'{self.post.id}'
                                                              }))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_index_page_context(self):
        """Тест контекста главной страницы"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = self.author
        post_group_0 = self.group
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_group_0, self.group)

    def test_group_list_page_context(self):
        """Тест контекста страницы группы"""
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug':
                                                      f'{self.group.slug}'}))
        response.context['group']
        group_0 = self.group
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = self.author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(group_0, self.group)

    def test_profile_page_context(self):
        """Тест контекста страницы профиля пользователя"""
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username':
                                                      f'{self.author.username}'
                                                      }))
        response.context['author']
        profile_author_0 = self.author
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = self.group
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(profile_author_0, self.author)

    def test_page_detail_context(self):
        """Тест контекста страницы конкретного поста"""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      f'{self.post.id}'}))
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_id_0, self.post.id)

    def test_create_page_context(self):
        """Тест контекста страницы создания поста"""
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
        """Тест контекста страницы редактирования поста"""
        edit_url = reverse('posts:post_edit', kwargs={'post_id':
                                                      f'{self.post.id}'})
        response = self.authorized_author.get(edit_url)
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_id_0, self.post.id)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_get_in_group(self):
        """Тест страницы создания поста с указанием группы"""
        post = Post.objects.create(
            author=self.author,
            text='Тестовый текст',
            group=self.group
        )
        response = {
            self.authorized_client.get(reverse('posts:index')),
            self.authorized_client.get(reverse('posts:group_list',
                                               kwargs={'slug':
                                                       f'{self.group.slug}'})),
            self.authorized_client.get(reverse(
                'posts:profile', kwargs={'username': f'{self.author.username}'
                                         }))
        }
        for resp in response:
            obj = resp.context.get('page_obj').object_list
            self.assertIn(post, obj)

    def test_post_get_another_group(self):
        """Тест пост не попал в группу, которой не предназначен"""
        post = Post.objects.create(
            author=self.author,
            text='Тестовый текст',
            group=None
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        obj = response.context.get('page_obj').object_list
        self.assertNotIn(post, obj)


class PaginatorViewsTest(TestCase):
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
        post_list = [
            (Post(
                text=f'тест паджинатора {i}',
                author=cls.author,
                group=cls.group,))
            for i in range(settings.PGN_RANGE)
        ]
        Post.objects.bulk_create(post_list)

    def setUp(self):
        self.client = Client()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_first_page_contains_ten_records(self):
        """Тест страницы паджинатора вывод 10 постов на 1 странице"""
        urls = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile', kwargs={'username':
                                             f'{self.author.username}'}),
        }
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']),
                             settings.PGN_1_PAGE)

    def test_second_page_contains_three_records(self):
        """Тест страницы паджинатора вывод 3 поста на 2 странице"""
        urls = {
            reverse('posts:index') + '?page=2',
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}) + '?page=2',
            reverse('posts:profile',
                    kwargs={'username':
                            f'{self.author.username}'}) + '?page=2',
        }
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']),
                             (settings.PGN_RANGE) - (settings.PGN_1_PAGE))
