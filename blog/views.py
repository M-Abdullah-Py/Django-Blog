from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import UserRegistrationForm, LoginForm, BlogPostForm, UserProfileEditForm
from .models import BlogPost, Category, Comment
from django.http import HttpResponseForbidden
from django.db.models import Q


# Home view
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from blog.models import BlogPost, Category
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from blog.models import BlogPost, Category
from django.db.models import Count

def home(request):
    context = {}

    # Check if the featured post exists
    try:
        featured_post = BlogPost.objects.get(sections="Featured")
        context["featured"] = {
            "title": featured_post.title,
            "author": featured_post.author,
            "image": featured_post.image,
            "category": featured_post.Category,
            "created_at": featured_post.created_at,
            "slug": featured_post.slug,
        }
    except BlogPost.DoesNotExist:
        context["featured"] = None  # No featured post available

    # Popular posts (only try to display if available)
    popular_posts = BlogPost.objects.order_by('-views').only('title', 'image', "created_at")[:10]
    context["populars_first"] = popular_posts[:4]
    context["populars"] = popular_posts[4:10]

    # Recent posts
    recent_posts = BlogPost.objects.order_by("-created_at").only('title', 'image', "created_at")[:8]
    context["recents"] = recent_posts

    # Editor pick (if available)
    editor_pick = BlogPost.objects.filter(sections="Editor Pick").select_related('Category').only(
        'title', 'image', 'created_at', 'author', 'Category__name', "slug"
    )[:7]
    context["featured_editor"] = editor_pick[0] if editor_pick else None
    context["editors"] = editor_pick[1:] if editor_pick else []

    # Trending posts from the last week
    one_week_ago = timezone.now() - timedelta(days=7)
    trending_posts = BlogPost.objects.filter(created_at__gte=one_week_ago).select_related('Category') \
        .only('title', 'image', 'created_at', 'author', 'Category__name').order_by('-views')[:6]
    context["trending_first"] = trending_posts[:3]
    context["trendings"] = trending_posts[3:]

    # Latest posts (if available)
    latest = BlogPost.objects.select_related('author') \
        .only('author__name', 'title', 'description', 'image', 'created_at') \
        .order_by("-created_at")[:5]
    context["latest_posts"] = latest
    print(latest)

    # Rest posts related to a specific category (if data is available)
    rest_posts = BlogPost.objects.filter(Category__name="Django Rest Framework").only("image", "author", "title", "created_at")
    context["rest_posts"] = rest_posts

    # Categories (ensure categories exist)
    categories = Category.objects.annotate(post_count=Count("blogpost"))
    context["categories"] = categories


    return render(request, "blog/home.html", context)


# Single post view
def single_post(request, slug):
    post = get_object_or_404(BlogPost.objects.prefetch_related("tags", "comments")
                             .select_related("Category").annotate(comment_count=Count('comments')), slug=slug)
    popular_posts = BlogPost.objects.order_by('-views').only('title', 'image', "created_at")[:3]
    categories = Category.objects.annotate(post_count=Count("blogpost"))
    rest_posts = BlogPost.objects.filter(Category__name="Django Rest Framework").only("image", "author", "title", "created_at")

    post_id = f'post_viewed_{post.id}'

    if not request.COOKIES.get(post_id):
        post.views += 1 
        post.save()
    
    response = render(request, "blog/single.html", {
        "post": post,
        "populars": popular_posts,
        "categories": categories,
        "rest_posts": rest_posts
    })

    response.set_cookie(post_id, True,max_age= 24* 60* 60)
    return response


# Commenting on a post
@login_required
def post_comment(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('InputComment')
        Comment.objects.create(blog=post, user=request.user, content=content)
        return redirect('post', slug=post.slug)
    return redirect('home')

# Blog posts list
def Blog_Posts(request):
    posts_list = BlogPost.objects.all()
    popular_posts = BlogPost.objects.order_by('-views').only('title', 'image', "created_at")[:3]
    categories = Category.objects.annotate(post_count=Count("blogpost"))
    paginator = Paginator(posts_list, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, "blog/blog.html", {"posts": posts, "popular_posts": popular_posts, "categories": categories})

# Posts by category
def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts_list = BlogPost.objects.filter(Category=category).only("title", "image", "created_at", "author", "description")
    popular_posts = BlogPost.objects.order_by('-views').only('title', 'image', "created_at")[:3]
    categories = Category.objects.annotate(post_count=Count('blogpost'))
    paginator = Paginator(posts_list, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'blog/category.html', {'category': category, 'posts': posts, 'popular_posts': popular_posts, 'categories': categories})

# Contact page
def contact(request):
    return render(request, "blog/contact.html")

# User registration
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            for error in form.errors:
                messages.error(request, form.errors[error])
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# User login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

# User logout
def logout_view(request):
    logout(request)
    return redirect('home')

# Create a blog post
@login_required
def create_blogpost(request):
    # Check if the user has the permission to create a post
    if not request.user.has_perm('blog.can_publish_blogpost'):
        return HttpResponseForbidden("You do not have permission to create a blog post.")  # You can customize this message or redirect to a different page

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user  # Assign the logged-in user as the author
            new_post.save()
            return redirect('post', slug=new_post.slug)  # Redirect to the new post's detail page
    else:
        form = BlogPostForm()  # Initialize an empty form if it's a GET request

    return render(request, 'posts/create_post.html', {'form': form})




# Profile view
@login_required
def profile(request):
    return render(request, "user/profile.html", context={"user": request.user})

# Edit profile
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileEditForm(instance=request.user)
    
    return render(request, 'user/edit_profile.html', {'form': form})

# Edit a blog post

@login_required
def edit_blogpost(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    # print(post.user)
    # print(request.user)

    # Check if the logged-in user is the owner of the post
    if post.author!= request.user:
        return HttpResponseForbidden("You do not have permission to edit this blog post.")

    # Check if the user has permission to edit the post (optional, if you want to enforce custom permissions)
    if not request.user.has_perm('blog.can_edit_blogpost'):
        return HttpResponseForbidden("You do not have permission to edit this blog post.")

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post', slug=post.slug)
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'posts/edit_posts.html', {'form': form, 'post': post})

# Delete a blog post
@login_required
def delete_blogpost(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    # Check if the logged-in user is the owner of the post
    if post.author != request.user:
        return HttpResponseForbidden("You do not have permission to delete this blog post.")

    # Check if the user has permission to delete the post (optional, if you want to enforce custom permissions)
    if not request.user.has_perm('blog.can_delete_blogpost'):
        return HttpResponseForbidden("You do not have permission to delete this blog post.")

    if request.method == 'POST':
        post.delete()
        return redirect('home')  # Redirect to the homepage after deletion

    return render(request, 'posts/confirm_delete.html', {'post': post})

# Display user posts
@login_required
def user_posts(request):
    posts = BlogPost.objects.filter(author=request.user)
    return render(request, 'user/user_posts.html', {'posts': posts})



def search_blogposts(request):
    query = request.GET.get('q', '')  # Get the search query from the GET request
    results = BlogPost.objects.none()  # Default to an empty queryset if no query is provided
    
    if query:
        # Perform a case-insensitive search for the query in title and content fields
        results = BlogPost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    
    return render(request, 'search_results.html', {'results': results, 'query': query})