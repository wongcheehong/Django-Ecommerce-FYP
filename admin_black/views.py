from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import admin
from django.template.response import TemplateResponse
from orders.models import Order, OrderItem
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay
from django.db.models import Sum, Count, Q, When
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F


@staff_member_required
def index(request):
    paid_orders = Order.objects.filter(
        paid=True, created__gte=datetime.now() - timedelta(days=30)
    ).annotate(
        date=TruncDay('created')
    ).order_by('date').values('date').annotate(total=Sum('amount'))

    order_counts = Order.objects.filter(
        paid=True, created__gte=datetime.now() - timedelta(days=7)
    ).annotate(
        date=TruncDay('created')
    ).order_by('date').values(
        'date',
    ).annotate(created_count=Count('created'))

    top_selling = OrderItem.objects.values(name=F('product__name')).annotate(quantity=Sum('quantity')).order_by('-quantity')[:8]

    order_status = Order.objects.aggregate(
        not_delivered_qtty=Count('paid', filter=(Q(being_delivered=False))),
        delivered_qtty=Count('being_delivered', filter=(Q(being_delivered=True))),
        completed_qtty=Count('received', filter=(Q(received=True))),
    )

    recent_orders = Order.objects.all().order_by('-updated')[:7]

    return render(request, 'admin/index.html', {
        'paid_orders': paid_orders,
        'order_counts': order_counts,
        'top_selling': top_selling,
        'order_status': order_status,
        'recent_orders': recent_orders,
        'title': admin.site.index_title})

