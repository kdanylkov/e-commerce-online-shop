from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponse, HttpRequest
from django.db.models import QuerySet
from django.db.models.options import Options

import datetime
import csv

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.action(description='Export to CSV')
def export_to_csv(modeladmin: admin.ModelAdmin,
                  request: HttpRequest, queryset: QuerySet):
    queryset = queryset.order_by('id')
    opts: Options = modeladmin.model._meta
    now = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')

    content_disposition = f'attachment; filename="orders_dump_{now}.csv"'

    response = HttpResponse(content_type='text/csv',
                            headers={
                                'Content-Disposition': content_disposition,
                                })

    writer = csv.writer(response)
    fields = [field for field in opts.get_fields()
              if not field.many_to_many and not field.one_to_many]

    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:

        data_row = []

        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y %H:%M:%S')
            data_row.append(value)

        writer.writerow(data_row)

    return response


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'order_detail', 'email',
                    'address', 'postal_code', 'city', 'paid', 'order_payment',
                    'created', 'order_detail', 'updated',]

    list_filter = ['paid', 'created', 'updated']
    list_display_links = ['first_name']
    inlines = [
        OrderItemInline,
    ]
    actions = [
        export_to_csv,
    ]

    @admin.display(boolean=False, description='Stripe payment')
    def order_payment(self, obj):
        url = obj.get_stripe_url()
        if obj.stripe_id:
            html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
            return mark_safe(html)
        return ''

    @admin.display(description='Order Details')
    def order_detail(self, obj):
        url = reverse('orders:admin_order_detail', args=[obj.id])
        return mark_safe(f'<a href="{url}">View</a>')
