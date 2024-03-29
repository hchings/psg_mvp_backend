"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include

from rest_framework_swagger.views import get_swagger_view

# swagger documentation setup
schema_view = get_swagger_view(title='Backend API Documentation')


internal_apis = [
    # url(r'^$', schema_view, name='swagger-root'),
    # path('admin/', admin.site.urls),
]

urlpatterns = internal_apis + [
    url(r'^$', schema_view, name='swagger-root'),
    path('admin/', admin.site.urls),
    url(r'activity/', include('actstream.urls')),
    url(r'auth/', include('users.urls')),
    url(r'accounts/', include('allauth.urls')),
    url(r'^clinics/', include('users.clinics.urls')),
    url(r'^cases/', include('cases.urls')),
    url(r'^reviews/', include('reviews.urls')),
    url(r'^comments/', include('comments.urls')),
    url(r'^doctors/', include('users.doctors.urls')),
    url(r'^tags/', include('tags.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
