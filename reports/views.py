from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, time
from decimal import Decimal
from django.db.models import Sum, Avg, Count, F, Q, Subquery, Value, DecimalField
from payments.models import Invoice, Payment
from orders.models import Order, OrderItem
from users.models import Staff
from core.decorators import admin_required
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.db.models import OuterRef


@admin_required
def sales_report(request):
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today

    if request.method == "GET":
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

    start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
    end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))

    invoices = Invoice.objects.filter(
        created_at__range=[start_datetime, end_datetime]
    ).exclude(inHold=True)

    total_sales = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal(0)
    num_orders = invoices.count()
    avg_order_value = invoices.aggregate(avg_value=Avg('total_amount'))['avg_value'] or Decimal(0)

    item_sales = (
        OrderItem.objects.filter(invoice__in=invoices)
        .values('item__name')
        .annotate(
            total_items_sold=Count('id'),
            total_revenue=Sum('price')
        )
        .order_by('-total_items_sold')
    )

    payments_in_range = Payment.objects.filter(
        created_at__range=[start_datetime, end_datetime],
        inHold=False
    )

    payment_method_summary = (
        payments_in_range.values('method')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    payment_labels = [p['method'] for p in payment_method_summary]
    payment_data = [float(p['total']) for p in payment_method_summary]

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'num_orders': num_orders,
        'avg_order_value': avg_order_value,
        'item_sales': item_sales,
        'payment_method_summary': payment_method_summary,
        'payment_labels': payment_labels,
        'payment_data': payment_data,
    }

    return render(request, 'sales_report.html', context)

@admin_required
def payment_report(request):
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today

    if request.method == "GET":
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError: pass

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError: pass

    start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
    end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))

    invoices_in_report = Invoice.objects.filter(
        Q(payments__created_at__range=[start_datetime, end_datetime]) |
        Q(created_at__range=[start_datetime, end_datetime]),
        inHold=False
    ).distinct()

    cash_subquery = Payment.objects.filter(invoice=OuterRef("pk"), method="CASH",inHold=False).values("invoice").annotate(total=Sum("amount")).values("total")
    bank_subquery = Payment.objects.filter(invoice=OuterRef("pk"), method="CARD",inHold=False).values("invoice").annotate(total=Sum("amount")).values("total")
    momo_subquery = Payment.objects.filter(invoice=OuterRef("pk"), method="MOMO",inHold=False).values("invoice").annotate(total=Sum("amount")).values("total")

    invoices_report = invoices_in_report.annotate(
        cash_total=Coalesce(Subquery(cash_subquery), Value(0), output_field=DecimalField()),
        bank_total=Coalesce(Subquery(bank_subquery), Value(0), output_field=DecimalField()),
        momo_total=Coalesce(Subquery(momo_subquery), Value(0), output_field=DecimalField()),
    ).annotate(
        total_paid=F("cash_total") + F("bank_total") + F("momo_total")
    ).order_by("-created_at")

    payments_in_range = Payment.objects.filter(
        created_at__range=[start_datetime, end_datetime],
        inHold=False
    )

    grand_totals_payments = payments_in_range.aggregate(
        total_paid=Sum('amount'),
        total_cash=Sum('amount', filter=Q(method='CASH')),
        total_bank=Sum('amount', filter=Q(method='CARD')),
        total_momo=Sum('amount', filter=Q(method='MOMO'))
    )

    total_billed = invoices_in_report.aggregate(total_billed=Sum('total_amount'))['total_billed'] or Decimal(0)

    grand_totals = {
        'total_billed': total_billed,
        'total_paid': grand_totals_payments.get('total_paid') or Decimal(0),
        'total_cash': grand_totals_payments.get('total_cash') or Decimal(0),
        'total_bank': grand_totals_payments.get('total_bank') or Decimal(0),
        'total_momo': grand_totals_payments.get('total_momo') or Decimal(0),
    }

    paginator = Paginator(invoices_report, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "grand_totals": grand_totals,
        "start_date_str": start_date.strftime("%Y-%m-%d") if start_date else "",
        "end_date_str": end_date.strftime("%Y-%m-%d") if end_date else "",
    }

    return render(request, "payment_report.html", context)

@admin_required
def staff_report(request):
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today

    if request.method == "GET":
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

    start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
    end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))

    staff_members = Staff.objects.filter(is_active=True).select_related('user')

    orders_served_query = Order.objects.filter(
        waiter=OuterRef('pk'),
        ordered_at__range=[start_datetime, end_datetime]
    ).values('waiter').annotate(count=Count('pk')).values('count')

    invoices_total_query = Invoice.objects.filter(
        created_by=OuterRef('user_id'),
        created_at__range=[start_datetime, end_datetime]
    ).values('created_by').annotate(total=Sum('total_amount')).values('total')

    staff_performance_data = staff_members.annotate(
        orders_served_count=Subquery(orders_served_query),
        invoices_created_total=Subquery(invoices_total_query)
    ).order_by('-invoices_created_total')

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'staff_performance_data': staff_performance_data,
    }

    return render(request, 'staff_report.html', context)
