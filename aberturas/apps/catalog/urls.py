from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    
    # Price Lists
    path('pricelists/', views.PriceListListView.as_view(), name='pricelist_list'),
    path('pricelists/create/', views.PriceListCreateView.as_view(), name='pricelist_create'),
    path('pricelists/<int:pk>/', views.PriceListDetailView.as_view(), name='pricelist_detail'),
    path('pricelists/<int:pk>/edit/', views.PriceListUpdateView.as_view(), name='pricelist_edit'),
    
    # Price List Rules
    path('pricelists/<int:pricelist_pk>/rules/', views.PriceListRuleListView.as_view(), name='pricelist_rules'),
    path('pricelists/<int:pricelist_pk>/rules/create/', views.PriceListRuleCreateView.as_view(), name='pricelistrule_create'),
    path('pricelists/<int:pricelist_pk>/rules/<int:pk>/edit/', views.PriceListRuleUpdateView.as_view(), name='pricelistrule_edit'),
    
    # Utilities
    path('pricing/preview/', views.pricing_preview, name='pricing_preview'),
]