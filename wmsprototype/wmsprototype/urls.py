"""
URL configuration for wmsprototype project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("home/", views.home, name="home"),
    path("actions/", views.actions, name="actions"),
    path("document/<int:document_id>/", views.view_document, name="view_document"),
    path("document/new/", views.select_document_type, name="new_document"),
    path("document/new/<str:doc_type>/", views.create_specific_document, name="create_specific_document"),
    path("document/all/", views.list_documents, name="list_documents"),
    path("product/<int:product_id>/", views.view_product, name="view_product"),
    path("product/all/", views.list_products, name="list_products")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
