from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET

from .models import Product, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


def redirect_home(request):
    return redirect('/shop/')


def homepage(request):
    products_list = Product.objects.filter(available=True)
    latest_products = products_list.order_by('-created')[:9]

    # paginator
    paginator = Paginator(products_list, 9)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        products = paginator.page(paginator.num_pages)

    return render(request, 'shop/homepage.html', {'section': 'home',
                                                  'products': products,
                                                  'latest_products': latest_products})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products_list = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products_list = Product.objects.filter(category=category)

    # paginator
    paginator = Paginator(products_list, 8)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        products = paginator.page(paginator.num_pages)

    return render(request, 'product/product_list.html', {'section': 'products',
                                                         'category_slug': category_slug,
                                                         'categories': categories,
                                                         'products': products
                                                         })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)

    return render(request, 'product/product_detail.html', {'product': product})


@require_GET
def product_search(request):
    categories = []
    if 'query' in request.GET:
        query = request.GET.get('query')
        search_vector = SearchVector('name', 'description', 'category__name')
        search_query = SearchQuery(query)
        products = Product.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query, available=True).order_by('-rank')

        categories = set([product.category for product in products])
        category_id = request.GET.get('category')
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            products = products.filter(category=category)

        # paginator
        paginator = Paginator(products, 8)
        page = request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            products = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            products = paginator.page(paginator.num_pages)

        return render(request, 'product/search_result.html', {'section': 'products',
                                                              'query': query,
                                                              'category_id': category_id,
                                                              'products': products,
                                                              'categories': categories})


def admin_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.available = False
    product.save()
    messages.success(request, "Product has been made unavailable")

    return redirect(request.META['HTTP_REFERER'])