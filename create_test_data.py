import os
import django
import sys
from django.utils.text import slugify
from django.utils import timezone

# Set UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Article, Author, Category, Comment
from django.contrib.auth.models import User

def create_test_data():
    # Clear existing data
    Comment.objects.all().delete()
    Article.objects.all().delete()
    Category.objects.all().delete()
    Author.objects.all().delete()

    # Create an author
    author = Author.objects.create(
        name="Ahmed Mohammed",
        bio="Technology writer and content editor",
        email="ahmed@example.com",
        website="https://ahmed-tech.com",
        twitter_handle="@ahmed_tech"
    )

    # Create categories
    categories = [
        Category.objects.create(
            name="Web Development",
            slug="web-development",
            description="Articles about web development",
            icon="🌐"
        ),
        Category.objects.create(
            name="Artificial Intelligence",
            slug="artificial-intelligence",
            description="Everything about AI and its applications",
            icon="🤖"
        )
    ]

    # Create articles
    for i in range(1, 6):
        article = Article.objects.create(
            title=f"Test Article {i}",
            slug=f"test-article-{i}",
            content=f"""This is test content for article {i}. This article contains valuable information
            about an important topic in technology. We hope you find it useful.
            
            You can use this content for testing and development.""" * 3,
            summary=f"Summary for test article {i}",
            author=author,
            category=categories[i % 2],
            status='published',
            pub_date=timezone.now(),
            featured=(i == 1)  # Make the first article featured
        )
        
        # Add some views and likes
        article.views = i * 100
        article.likes = i * 10
        article.save()

        # Create some comments
        for j in range(2):
            Comment.objects.create(
                article=article,
                user=User.objects.get(username='admin'),
                text=f"Test comment {j+1} on article {i}",
                is_approved=True
            )

if __name__ == '__main__':
    create_test_data()
    print("Test data created successfully")
