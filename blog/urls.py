from django.contrib.sitemaps.views import sitemap
from django.urls import path
from blog.sitemaps import PostSitemap

from . import views

from .feeds import LatestPostsFeed

app_name = 'blog'

sitemaps = {
 'posts': PostSitemap,
}

urlpatterns = [
    # post views
    path('', views.post_list, name='post_list'),
    # id views
    path('<int:id>/', views.post_detail_id, name='post_detail_id'),
    # year-month-view
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',views.post_detail,name='post_detail'),
    #function Based View
    path('list/', views.post_list, name='post_list'),
    # class Based view
    #path('', views.PostListView.as_view(), name='post_list_view'),
    # Email view
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    # Comment View
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
]









