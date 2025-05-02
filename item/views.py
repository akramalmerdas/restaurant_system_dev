from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Item, Category, Extra
from .forms import ItemForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect  # <-- Add 'redirect' here
from django.contrib import messages  # <-- Add this import
from django.contrib.auth.mixins import LoginRequiredMixin


class ItemDashboardView(LoginRequiredMixin,ListView):
    model = Item
    template_name = 'item/item_dashboard.html'
    context_object_name = 'items'
    paginate_by = 10
  
    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').filter(inHold=False).order_by('category__name', 'name')
        category_id = self.request.GET.get('category_id')
        search_query = self.request.GET.get('search')

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(inHold=False).order_by('name')
        context['selected_category_id'] = self.request.GET.get('category_id', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ItemCreateView(LoginRequiredMixin,CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'item/item_form.html'
    success_url = reverse_lazy('item:item_dashboard')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = 'Create New Item'
        context['extras'] = Extra.objects.all()
        return context

class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'item/item_form.html'
    success_url = reverse_lazy('item:item_dashboard')
    context_object_name = 'item'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_title'] = f'Update Item: {self.object.name}'
        context['extras'] = Extra.objects.all()
        return context

def item_delete_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.inHold = True
        item.save()
        messages.success(request, f'Item "{item.name}" was deleted successfully.')
        return redirect(reverse('item:item_dashboard'))
    print('going to the delete page')
    return render(request, 'item/item_dashboard.html', {'item': item})
   