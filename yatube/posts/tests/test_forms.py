import shutil
import tempfile

from django.conf import settings
from http import HTTPStatus
from django.test import Client, override_settings
from django.urls import reverse
from django import forms
from django.contrib.auth import get_user_model

from ..forms import PostForm
from ..models import Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(forms.ModelForm):
    """Форма для создания поста."""
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных для проверки сушествующего slug
        Post.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            slug='first'
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'slug': 'first',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                slug='testovyij-zagolovok',
                text='Тестовый текст',
            ).exists()
        )

    def test_cant_create_existing_slug(self):
        tasks_count = Post.objects.count()
        form_data = {
            'title': 'Заголовок из формы',
            'text': 'Текст из формы',
            'slug': 'first',
        }
        response = self.guest_client.post(
            reverse('deals:home'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertFormError(
            response,
            'form',
            'slug',
            'Адрес "first" уже существует, придумайте уникальное значение'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
