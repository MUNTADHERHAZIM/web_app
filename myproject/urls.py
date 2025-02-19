"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Authentication URLs
# path('login/', auth_views.LoginView.as_view(template_name='myapp/auth/login.html'), name='login'),
# path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
# path('password-change/', auth_views.PasswordChangeView.as_view(template_name='myapp/auth/password_change.html'), name='password_change'),
# path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='myapp/auth/password_change_done.html'), name='password_change_done'),

# تخصيص صفحات الخطأ
handler404 = 'myapp.views.handler404'
handler500 = 'myapp.views.handler500'
