from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .models import Group, Post
from .forms import PostForm

COUNTER_POSTS = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, COUNTER_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Главная страница Yatube',
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, COUNTER_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': group.title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(
        author__username=username).all()
    paginator = Paginator(post_list, COUNTER_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user_profile': user_profile,
        'username': username,
        'title': f'Профайл пользователя {username}',
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_text = post.text[:30]
    context = {
        'title': f'Пост {post_text}',
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form, 'title': 'Новый пост'})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect(f'/profile/{request.user}/')


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
                      'form': form,
                      'title': 'Редактировать пост',
                      'is_edit': True,
                      'post': post})
    form.save()
    return redirect('posts:post_detail', post_id)
