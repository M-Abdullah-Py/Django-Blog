from .models import Category
# from .models import BlogPost

# def trending_posts(request):
#     # Use the BlogPostManager's trending method to fetch trending posts
#     trending_posts = BlogPost.objects.trending()  # Uses the trending method
#     return {'trending_posts': trending_posts}


def categories(request):
    categories = Category.objects.values("slug", "name")[:5]
    return {'categories': categories}
