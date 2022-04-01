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
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group_2.id,
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
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста гостя',
            'group': self.group.id,
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_client_no_edit(self):
        """При POST запросе гостя пост не будет отредактирован"""
        form_data = {
            'text': 'Редактированный текст поста гостя',
            'group': self.group,
        }
        post = self.post
        self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        same_post = Post.objects.get(id=self.post.id)
        self.assertEqual(same_post.text, post.text)
        self.assertEqual(same_post.group, post.group)
        self.assertEqual(same_post.author, post.author)
        self.assertEqual(same_post.pub_date, post.pub_date)

    def test_auth_user_no_author_no_edit(self):
        """Авторизованный юзер, но не автор, не может редактировать."""
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group,
            'author': self.author,
        }
        post = self.post
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        same_post = Post.objects.get(id=self.post.id)
        self.assertEqual(same_post.text, post.text)
        self.assertEqual(same_post.group, post.group)
        self.assertEqual(same_post.author, post.author)
        self.assertEqual(same_post.pub_date, post.pub_date)

    def test_post_create_without_group(self):
        """Создание нового поста без указания группы"""
        posts_count = Post.objects.all().count()
        form_data = {
            'text': 'Тестовый текст в форме',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        last_post = Post.objects.latest('pub_date')
        self.assertEqual(posts_count + 1, Post.objects.all().count())
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.user)
        self.assertEqual(last_post.group, None)

    def test_change_text_other_fields_same(self):
        """При редактировании текста не меняются другие поля"""
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group,
        }
        post = self.post
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        self.authorized_author.post(
            url,
            data=form_data,
            follow=True
        )
        same_post = Post.objects.get(id=self.post.id)
        self.assertEqual(same_post.text, post.text)
        self.assertEqual(same_post.group, post.group)
        self.assertEqual(same_post.author, post.author)
        self.assertEqual(same_post.pub_date, post.pub_date)
