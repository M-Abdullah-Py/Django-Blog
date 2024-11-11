from blog.views import *
from django.urls import path

urlpatterns = [
    # Home
    path('', home, name="home"),
    
    # Blog Posts
    path('blog/', Blog_Posts, name="blog_posts"),
    path('posts/<slug:slug>/', single_post, name='post'),
    path('category/<slug:slug>/', category_posts, name='category_posts'),
    
    # User Profile
    path('profile/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    
    # User Posts
    path('create_post/', create_blogpost, name='create_post'),
    path('my-posts/', user_posts, name='user_posts'),
    path('edit-post/<slug:slug>/', edit_blogpost, name='edit_post'),
    path('delete-post/<slug:slug>/', delete_blogpost, name='delete_post'),
    
    # Comments
    path('comments/<int:post_id>/comment/', post_comment, name='post_comment'),
    
    # Authentication
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Miscellaneous
    path('contact/', contact, name='contact'),
    # path('check_permission/', publish_blogpost, name='publish'),
    path('search/', search_blogposts, name='search_blogposts'),
]
