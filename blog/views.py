from django.core.paginator import  EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Post
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm,SearchForm
from django.contrib.postgres.search import SearchVector
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.postgres.search import (SearchVector,SearchQuery,SearchRank)
from django.db.models import Q



def post_list(request,tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug =tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list,3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(
        request,
        'blog/post/list.html',
        {'posts': posts,
         'tag': tag
         }
    )
def post_detail_id(request, id):
    post = get_object_or_404(
    Post,
    id=id,
    status=Post.Status.PUBLISHED
    )
    return render(
    request,
    'blog/post/detail.html',
    {'post': post}
    )

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day)

    comments = post.comments.filter(active=True)
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags', '-publish')[:4]

    return render(
        request,
        'blog/post/detail.html',
        {'post': post,
         'comments':comments,
         'form':form,
         'similar_posts': similar_posts

         }
    )

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,id=post_id,status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_query = SearchQuery(query)
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_rank = SearchRank(search_vector, search_query)
            search_similarity = TrigramSimilarity('title', str(search_query))
            results = Post.published.annotate(rank=search_rank, similarity=search_similarity) .filter(Q(rank__gte=0.1) | Q(similarity__gte=0.1)) .order_by('-rank', '-similarity')

            for post in results:
                print(f"Title: {post.title}, Similarity: {post.similarity}, Rank: {post.rank}")
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})













































'''
from django.shortcuts import get_object_or_404, render

from .models import Post
from django.core.paginator import Paginator

def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
    return render(
        request,
        'blog/post/list.html',
        {'posts': posts}
    )

def post_detail_1(request, id):
    post = get_object_or_404(
        Post,
        id=id,
        status=Post.Status.PUBLISHED
    )
    return render(
        request,
        'blog/post/detail.html',
        {'post': post}
    )


def post_detail_2(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day)
    return render(
        request,
        'blog/post/detail.html',
        {'post': post}
    )
    
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_query = SearchQuery(query)
            search_vector = SearchVector('title',weight="A")+ SearchVector('body',weight="B")
            search_rank = SearchRank(search_vector,search_query)
            search_similarity = TrigramSimilarity ('title',str(search_query))
            results = Post.published.annotate( rank=search_rank,similarity=search_similarity).filter(Q(rank__gte=0.1) |Q(similarity__gte=0.1)).order_by("-rank","-similarity")
            rating = Post.published.annotate( rank=search_rank,similarity=search_similarity).order_by ("-rank","-similarity")
            print(rating)
    return render (request,'blog/post/search.html',{'form': form,'query': query,'results': results})
'''
