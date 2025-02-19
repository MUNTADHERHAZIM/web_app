from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.template.loader import get_template, render_to_string
from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings
import pdfkit
import json
import uuid
from .models import (
    Article, Category, Comment, NewsletterSubscription,
    ArticleAnalytics, Author, UserProfile, ReadingProgress
)

def home(request):
    featured_articles = Article.objects.filter(
        status='published',
        featured=True
    ).select_related('author', 'category').order_by('-pub_date')[:5]
    
    latest_articles = Article.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-pub_date')[:10]
    
    popular_articles = Article.objects.filter(
        status='published'
    ).order_by('-views')[:5]
    
    categories = Category.objects.annotate(
        article_count=Count('articles')
    ).order_by('-article_count')[:10]
    
    context = {
        'featured_articles': featured_articles,
        'latest_articles': latest_articles,
        'popular_articles': popular_articles,
        'categories': categories,
    }
    return render(request, 'myapp/home.html', context)

def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related('author', 'category'),
        slug=slug,
        status='published'
    )
    
    # Increment views
    article.views += 1
    article.save()
    
    # Get or create analytics
    analytics, created = ArticleAnalytics.objects.get_or_create(article=article)
    
    # Get related articles
    related_articles = Article.objects.filter(
        status='published',
        category=article.category
    ).exclude(id=article.id)[:3]
    
    # Get comments with replies
    comments = Comment.objects.filter(
        article=article,
        parent__isnull=True,
        is_approved=True
    ).select_related('user').prefetch_related('replies')
    
    context = {
        'article': article,
        'comments': comments,
        'related_articles': related_articles,
        'reading_time': article.get_reading_time(),
    }
    return render(request, 'myapp/article_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(
        category=category,
        status='published'
    ).select_related('author')
    
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, 'myapp/category_detail.html', context)

def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    articles = Article.objects.filter(
        author=author,
        status='published'
    ).select_related('category')
    
    stats = {
        'total_articles': articles.count(),
        'total_views': sum(article.views for article in articles),
        'avg_likes': articles.aggregate(Avg('likes'))['likes__avg'] or 0,
    }
    
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    context = {
        'author': author,
        'articles': articles,
        'stats': stats,
    }
    return render(request, 'myapp/author_detail.html', context)

def search_articles(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    author = request.GET.get('author', '')
    sort = request.GET.get('sort', '-pub_date')
    
    articles = Article.objects.filter(status='published')
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__icontains=query)
        )
    
    if category:
        articles = articles.filter(category__slug=category)
    
    if author:
        articles = articles.filter(author__id=author)
    
    # Sorting
    if sort == 'views':
        articles = articles.order_by('-views')
    elif sort == 'likes':
        articles = articles.order_by('-likes')
    else:
        articles = articles.order_by('-pub_date')
    
    articles = articles.select_related('author', 'category')
    
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    context = {
        'articles': articles,
        'query': query,
        'selected_category': category,
        'selected_author': author,
        'sort': sort,
        'categories': Category.objects.all(),
        'authors': Author.objects.all(),
    }
    return render(request, 'myapp/search_results.html', context)

@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update profile
        profile.bio = request.POST.get('bio', '')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        # Update interests
        interests = request.POST.getlist('interests')
        profile.interests.set(interests)
        
        profile.save()
        messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
        return redirect('myapp:user_profile')
    
    context = {
        'profile': profile,
        'categories': Category.objects.all(),
    }
    return render(request, 'myapp/user_profile.html', context)

@require_POST
@login_required
def add_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)
    data = json.loads(request.body)
    text = data.get('text')
    
    if text:
        comment = Comment.objects.create(
            user=request.user,
            article=article,
            text=text
        )
        return JsonResponse({
            'status': 'success',
            'username': comment.user.username,
            'text': comment.text,
            'created_date': comment.created_date.strftime('%d/%m/%Y')
        })
    return JsonResponse({'status': 'error', 'message': 'No text provided'})

@require_POST
@login_required
def track_reading_progress(request, slug):
    article = get_object_or_404(Article, slug=slug)
    data = json.loads(request.body)
    progress = data.get('progress', 0)
    time_spent = data.get('timeSpent', 0)
    
    # Update reading progress in the database
    ReadingProgress.objects.update_or_create(
        user=request.user,
        article=article,
        defaults={
            'progress': progress,
            'time_spent': time_spent
        }
    )
    return JsonResponse({'status': 'success'})

def generate_pdf(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    # Configure pdfkit path
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    
    # Render the template to HTML
    html = render_to_string('myapp/pdf/article.html', {'article': article})
    
    # Configure pdfkit options
    options = {
        'page-size': 'A4',
        'margin-top': '2cm',
        'margin-right': '2cm',
        'margin-bottom': '2cm',
        'margin-left': '2cm',
        'encoding': 'UTF-8',
        'enable-local-file-access': None,
        'direction': 'rtl',
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ]
    }
    
    # Generate PDF from HTML
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    
    # Create response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{article.slug}.pdf"'
    return response

@csrf_exempt
@login_required
def newsletter_signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        full_name = data.get('full_name', '')
        frequency = data.get('frequency', 'weekly')
        
        if email:
            # Generate confirmation token
            confirmation_token = str(uuid.uuid4())
            
            subscription, created = NewsletterSubscription.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': full_name,
                    'frequency': frequency,
                    'confirmation_token': confirmation_token
                }
            )
            
            if created:
                # Send confirmation email
                subject = 'تأكيد الاشتراك في النشرة البريدية'
                html_message = render_to_string('myapp/email/newsletter_confirmation.html', {
                    'subscription': subscription,
                    'token': confirmation_token
                })
                plain_message = strip_tags(html_message)
                
                try:
                    send_mail(
                        subject,
                        plain_message,
                        'noreply@example.com',
                        [email],
                        html_message=html_message
                    )
                    return JsonResponse({
                        'status': 'success',
                        'message': 'تم إرسال رسالة التأكيد إلى بريدك الإلكتروني'
                    })
                except Exception as e:
                    subscription.delete()
                    return JsonResponse({
                        'status': 'error',
                        'message': 'حدث خطأ أثناء إرسال رسالة التأكيد'
                    })
            
            return JsonResponse({
                'status': 'info',
                'message': 'أنت مشترك بالفعل في النشرة البريدية'
            })
        
        return JsonResponse({
            'status': 'error',
            'message': 'البريد الإلكتروني مطلوب'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'طريقة غير صالحة'
    })

def confirm_subscription(request, token):
    subscription = get_object_or_404(
        NewsletterSubscription,
        confirmation_token=token,
        is_active=False
    )
    
    subscription.is_active = True
    subscription.confirmation_token = ''
    subscription.save()
    
    messages.success(request, 'تم تأكيد اشتراكك في النشرة البريدية بنجاح')
    return redirect('myapp:home')

def handler404(request, exception):
    return render(request, 'myapp/errors/404.html', status=404)

def handler500(request):
    return render(request, 'myapp/errors/500.html', status=500)
