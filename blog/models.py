from django.db import models
from blog.managers import *
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.username.capitalize()

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null= True,blank=True)
    
    def __str__(self):
        return self.name
    
# Custom Manager for BlogPost
class BlogPostManager(models.Manager):
    def published(self):
        return self.filter(status="1")  # Filters for published posts

    def by_section(self, section_name):
        return self.published().filter(sections=section_name)  # Filters for published posts in a specific sectio
    
    def trending(self):
        """Fetches the top 5 trending posts based on views from the last 7 days"""
        one_week_ago = timezone.now() - timedelta(days=7)
        return self.published().filter(created_at__gte=one_week_ago) \
            .select_related('Category') \
            .only('title', 'image', 'created_at', 'author', 'Category__name') \
            .order_by('-views')[:5]

class BlogPost(models.Model):

    STATUS = (
       ('0',"Draft"),
       ('1',"Publish"),
    )
    
    SECTION = (
       ("Featured", "Featured"),
       ("Editor Pick", "Editor Pick"),
       ("Latest", "Latest"),
       ("Inspiration", "Inspiration"),
       ("Popular", "Popular"),
    )


    title = models.CharField(max_length=100)
    author = models.ForeignKey(User,on_delete=models.CASCADE, related_name="posts",null=True,blank=True)
    image = models.ImageField(upload_to="images")
    description = models.TextField()
    slug = models.SlugField(unique=True)
    content = RichTextUploadingField()
    views = models.IntegerField(default=0) 
    sections = models.CharField(choices=SECTION, max_length= 200, default="Latest")
    status = models.CharField(choices=STATUS, max_length=100)
    created_at = models.DateField(auto_now_add=True)
    Category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="blogpost")
   
    objects = BlogPostManager()

    class Meta:
        permissions = [
            ("can_publish_blogpost", "Can publish blog post"),  # Custom example
            ("can_edit_blogpost", "Can edit blog post"),
            ("can_delete_blogpost", "Can delete blog post"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super(BlogPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class Tag(models.Model):
    name = models.CharField(max_length=25)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='tags') 

    def __str__(self):
        return self.name
    

class Comment(models.Model):
    content = models.TextField()
    blog = models.ForeignKey(BlogPost,on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"

# class BlogImages(models.Model):
#     blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="blog-images", null=True, blank=True)
#     images = models.ImageField(upload_to='featureimages/blog/')