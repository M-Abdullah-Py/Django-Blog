from django.contrib import admin
from .models import BlogPost, Category, Tag, Comment, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Inline admin for Tag model
class TagInline(admin.TabularInline):  # You can also use StackInline for a different layout
    model = Tag
    extra = 1 

# Custom admin class for BlogPost
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'views', 'slug', 'Category')  # Include Category in the list
    search_fields = ('title', 'author', 'content')  # Fields to search in admin
    prepopulated_fields = {'slug': ('title',)}  # Automatically generate the slug from the title field
    list_filter = ('status', 'sections')  # Filter options in the admin
    inlines = [TagInline]

# Admin class for Comment model
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'created_at', 'content')

# Custom admin for User with additional fields
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('name', 'bio', 'image')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('name', 'bio', 'image')}),
    )

# Admin class for Category model
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {'slug': ('name',)}

# Register models with the custom admin classes
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, CustomUserAdmin)
