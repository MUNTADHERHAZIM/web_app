from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Author, Category, Comment, NewsletterSubscription, ArticleAnalytics, ReadingProgress

# Register your models here.

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_image', 'bio', 'twitter_handle')
    search_fields = ('name', 'bio')
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.image.url)
        return "لا توجد صورة"
    display_image.short_description = 'الصورة الشخصية'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'display_image')
    search_fields = ('name',)
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "لا توجد صورة"
    display_image.short_description = 'صورة التصنيف'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'pub_date', 'views', 'likes', 'display_image')
    list_filter = ('category', 'author', 'pub_date')
    search_fields = ('title', 'content')
    date_hierarchy = 'pub_date'
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit: cover;" />', obj.image.url)
        return "لا توجد صورة"
    display_image.short_description = 'صورة المقال'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('text', 'user__username')

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_date')
    search_fields = ('email',)

@admin.register(ArticleAnalytics)
class ArticleAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('article', 'created_date', 'last_updated')
    list_filter = ('created_date',)

@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'progress', 'time_spent', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('user__username', 'article__title')
