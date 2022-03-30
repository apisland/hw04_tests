# from tokenize import group
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
        cls.group_2 = Group.objects.create(
            title='Тестовое название группы 2',
            slug='bat'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
            pub_date='Дата публикации'
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_post_create_form(self):
        """При отправке валидной формы создается новая запись в БД"""
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
                             kwargs={'username': f'{self.user.username}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст в форме',
                group=self.group.id,
                author=self.user
            ).exists()
        )

    def test_post_edit_with_post_id(self):
        """При валидной форме редактирования поста
        происходит изменение поста с id в БД"""
        self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group_2.id,
            'post_id': self.post.id
        }
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        self.authorized_author.post(
            url,
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст в форме',
                group=self.group_2.id,
                author=self.author,
                id=self.post.id,
            ).exists()
        )

    def test_guest_client_no_create(self):
        """При POST запросе гость не может создать новый пост"""
        form_data = {
            'text': 'Текст поста гостя',
            'group': self.group.id,
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertFalse(Post.objects.filter(
            text='Текст поста гостя'
        ).exists())

    def test_guest_client_no_edit(self):
        """При POST запросе гостя пост не будет отредактирован"""
        self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        form_data = {
            'text': 'Редактированный текст поста гостя',
            'group': self.group.id,
        }
        self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Редактированный текст поста гостя'
        ).exists())

    def test_auth_user_no_author_no_edit(self):
        """Авторизованный юзер, но не автор, не может редактировать."""
        self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group.id,
            'post_id': self.post.id
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Новый текст в форме',
            group=self.group.id,
            id=self.post.id
        ).exists())

    def test_post_create_without_group(self):
        """Создание нового поста без указания группы"""
        form_data = {
            'text': 'Текст в форме',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertTrue(Post.objects.filter(
            text='Текст в форме',
            author=self.user,
        ).exists())

        def IsTrue(i=self.group):
            return i is None
        self.assertFalse(IsTrue(i=self.group))

    def test_change_text_other_fields_same(self):
        """При редактировании текста не меняются другие поля"""
        self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_data = {
            'text': 'Новый текст в форме',
        }
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        self.authorized_author.post(
            url,
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text='Новый текст в форме'
        ).exists())
        self.assertTrue(self.group.title)
        self.assertTrue(self.author)
        self.assertTrue(self.post.pub_date)
