from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
import readtime

def validate_image_size(image):
    filesize = image.size
    megabyte_limit = 5.0
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"الحد الأقصى لحجم الصورة هو {megabyte_limit} ميجابايت")

class Author(models.Model):
    name = models.CharField(max_length=200, validators=[MinLengthValidator(2, "يجب أن يحتوي الاسم على حرفين على الأقل")])
    bio = models.TextField(help_text="نبذة عن الكاتب")
    image = models.ImageField(
        upload_to='authors/',
        null=True,
        blank=True,
        validators=[validate_image_size],
        help_text="الحد الأقصى لحجم الصورة 5 ميجابايت"
    )
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True, help_text="الموقع الشخصي للكاتب")
    twitter_handle = models.CharField(max_length=50, blank=True)
    joined_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-joined_date']
        verbose_name = "كاتب"
        verbose_name_plural = "الكتّاب"
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('myapp:author_detail', args=[str(self.id)])

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="اسم الأيقونة من Bootstrap Icons", default="book")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text="صورة التصنيف")
    
    class Meta:
        ordering = ['name']
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('myapp:category_detail', args=[str(self.slug)])

class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('published', 'منشور'),
        ('archived', 'مؤرشف')
    ]
    
    title = models.CharField(max_length=200, validators=[MinLengthValidator(5, "العنوان قصير جداً")])
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(validators=[MinLengthValidator(100, "المحتوى قصير جداً")])
    summary = models.TextField(max_length=300, help_text="ملخص قصير للمقال", blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    tags = models.CharField(max_length=500, help_text="الوسوم مفصولة بفواصل", blank=True)
    featured_image = models.ImageField(
        upload_to='articles/',
        null=True,
        blank=True,
        validators=[validate_image_size],
        help_text="الصورة الرئيسية للمقال"
    )
    image = models.ImageField(upload_to='articles/%Y/%m/', blank=True, null=True, help_text="صورة المقال")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    pub_date = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    allow_comments = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, help_text="عرض في القسم المميز")
    
    def clean(self):
        if self.image:
            # التحقق من حجم الصورة
            if self.image.size > 5 * 1024 * 1024:  # 5 ميجابايت
                raise ValidationError("حجم الصورة يجب أن يكون أقل من 5 ميجابايت")
            
            # التحقق من أبعاد الصورة
            from PIL import Image
            img = Image.open(self.image)
            if img.width > 2000 or img.height > 2000:
                raise ValidationError("أبعاد الصورة يجب أن تكون أقل من 2000×2000 بكسل")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-pub_date']
        verbose_name = "مقال"
        verbose_name_plural = "المقالات"
        indexes = [
            models.Index(fields=['pub_date', 'status']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('myapp:article_detail', args=[str(self.slug)])
    
    def get_reading_time(self):
        return readtime.of_text(self.content)
    
    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    text = models.TextField(validators=[MinLengthValidator(5, "التعليق قصير جداً")])
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    likes = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = "تعليق"
        verbose_name_plural = "التعليقات"
    
    def __str__(self):
        return f'تعليق من {self.user.username} على {self.article.title}'

class NewsletterSubscription(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('daily', 'يومية'),
        ('weekly', 'أسبوعية'),
        ('monthly', 'شهرية')
    ]
    
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default='weekly')
    subscribed_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    confirmation_token = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "اشتراك النشرة البريدية"
        verbose_name_plural = "اشتراكات النشرة البريدية"
    
    def __str__(self):
        return self.email

class ArticleAnalytics(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='analytics')
    read_progress = models.JSONField(default=dict)
    interaction_data = models.JSONField(default=dict)
    created_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    bounce_rate = models.FloatField(default=0)
    avg_time_spent = models.DurationField(null=True, blank=True)
    social_shares = models.JSONField(default=dict)
    device_stats = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = "تحليلات المقال"
        verbose_name_plural = "تحليلات المقالات"
    
    def __str__(self):
        return f'تحليلات {self.article.title}'

class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progress')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reading_progress')
    progress = models.IntegerField(default=0)  # Percentage of article read
    time_spent = models.IntegerField(default=0)  # Time spent reading in seconds
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'article')
        verbose_name = 'تقدم القراءة'
        verbose_name_plural = 'تقدم القراءة'

    def __str__(self):
        return f"{self.user.username} - {self.article.title} ({self.progress}%)"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[validate_image_size])
    interests = models.ManyToManyField(Category, blank=True, related_name='interested_users')
    favorite_articles = models.ManyToManyField(Article, blank=True, related_name='favorited_by')
    notification_preferences = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"
    
    def __str__(self):
        return f'ملف {self.user.username}'
