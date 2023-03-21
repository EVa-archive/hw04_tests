from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    """Форма для создания поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='NoName',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1,
                         'Поcт не добавлен в базу данных'
                         )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост',
                group=self.group.id,
                author=self.user
            ).exists(), 'Данные поста не совпадают'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_cant_create_existing_slug(self):
        '''Проверка изменения поста в БД'''
        posts_count = Post.objects.count()
        self.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        form_data = {
            'text': 'Текст записанный в форму',
            'group': self.group_2.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        group=self.group_2.id,
                        author=self.user,
                        pub_date=self.post.pub_date
                        ).exists(), 'Данные поста не совпадают')
        self.assertNotEqual(self.post.text, form_data['text'],
                            'Невозможно изменить содержание поста')
        self.assertNotEqual(self.post.group, form_data['group'],
                            'Невозможно изменить группу поста')
        self.assertNotEqual(Post.objects.count(),
                            posts_count + 1,
                            'Поcт добавлен в БД')
