from etc.admin import CustomModelPage
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models

from procurement_supply.models import User, Category, Product, Supplier, Stock, Characteristic, ProductCharacteristic, \
    Purchaser, ChainStore, ShoppingCart, CartPosition, OrderPosition, Order
from procurement_supply.tasks import do_import

admin.site.site_header = 'Procurement Supply Review Admin'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal info", {"fields": (("first_name", "last_name"), ('company', 'position'), 'type')}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    ("is_staff",
                    "is_superuser"),
                    "groups",
                ),
            },
        ),
        ("Important dates", {"fields": (("last_login", "date_joined"),)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", 'email',
                           ("first_name", 'last_name'),
                           ('company', 'position'),
                           'type'),
            },
        ),
    )
    list_display = ('id', "username", "email", "first_name", "last_name", 'company', 'position')
    list_filter = ('type', "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email", 'company', 'position')
    readonly_fields = ('type', 'is_staff', 'is_superuser', "last_login", "date_joined")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CategorySupplierInline(admin.TabularInline):
    model = Category.suppliers.through
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)
    inlines = [CategorySupplierInline, ]
    exclude = ('suppliers', )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category', )
    search_fields = ('name', 'category')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'order_status', 'user')
    list_filter = ('order_status', )
    search_fields = ('name', 'address')
    inlines = [CategorySupplierInline, ]
    readonly_fields = ('user', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic
    extra = 0


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    search_fields = ('name', )

    def has_delete_permission(self, request, obj=None):
        return False


class CartPositionInline(admin.TabularInline):
    model = CartPosition
    extra = 0
    fields = ('shopping_cart', 'stock', 'quantity', 'price', 'amount')
    readonly_fields = ('shopping_cart', 'stock', 'quantity', 'price', 'amount')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(stock__supplier__user=request.user)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderPositionInline(admin.TabularInline):
    model = OrderPosition
    extra = 0
    fields = ('order', 'stock', 'quantity', 'price', 'amount', 'confirmed', 'delivered')
    readonly_fields = ('order', 'stock', 'quantity', 'price', 'amount')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(order__status='saved', stock__supplier__user=request.user)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'model', 'product', 'supplier', 'description', 'price', 'price_rrc', 'quantity')
    list_filter = ('product', 'supplier')
    search_fields = ('sku', 'model', 'description')
    inlines = [ProductCharacteristicInline, CartPositionInline, OrderPositionInline]
    readonly_fields = ('product', 'supplier')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(supplier__user=request.user.id)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ChainStoreInline(admin.TabularInline):
    model = ChainStore
    extra = 0
    readonly_fields = ('name', 'address', 'phone')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Purchaser)
class PurchaserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'user')
    search_fields = ('name', 'address')
    inlines = [ChainStoreInline, ]
    readonly_fields = ('name', 'address', 'user')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChainStore)
class ChainStoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'phone', 'purchaser')
    list_filter = ('purchaser',)
    search_fields = ('name', 'address')
    readonly_fields = ('name', 'address', 'phone', 'purchaser')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchaser', 'total_quantity', 'total_amount')
    search_fields = ('purchaser', )
    fields = ("purchaser", "total_quantity", 'total_amount')
    readonly_fields = ('purchaser', "total_quantity", 'total_amount')
    inlines = [CartPositionInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(cart_positions__stock__supplier__user=request.user).distinct()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CartPosition)
class CartPositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'shopping_cart', 'stock', 'price', 'quantity', 'amount')
    list_filter = ('shopping_cart', 'stock')
    search_fields = ('stock',)
    readonly_fields = ('shopping_cart', 'stock', 'price', 'quantity', 'amount')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(stock__supplier__user=request.user)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ("purchaser", 'date', "total_quantity", 'total_amount',
              'confirmed', 'delivered', 'chain_store', 'status')
    list_display = ('id', 'purchaser', 'date', 'total_quantity', 'total_amount',
                    'status', 'confirmed', 'delivered', 'chain_store')
    list_filter = ('purchaser', 'status', 'chain_store')
    search_fields = ('purchaser', )

    readonly_fields = ('purchaser', 'date', "total_quantity", 'total_amount',
                       'confirmed', 'delivered', 'chain_store', 'status')
    inlines = [OrderPositionInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(order_positions__stock__supplier__user=request.user).distinct()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderPosition)
class OrderPositionAdmin(admin.ModelAdmin):
    fields = ('order', 'stock', 'quantity', 'price', 'amount', 'confirmed', 'delivered')
    readonly_fields = ('order', 'stock', 'quantity', 'price', 'amount')
    list_display = ('id', 'order', 'stock', 'quantity', 'price', 'amount', 'confirmed', 'delivered')
    list_filter = ('order', 'stock')
    search_fields = ('stock',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(order__status='saved', stock__supplier__user=request.user)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ImportStocks(CustomModelPage):
    title = 'Import stocks'

    url = models.CharField('url', max_length=500)

    def save(self):
        res = do_import.delay(self.url)

        self.bound_admin.message_success(self.bound_request, f'Import started. Task id to get result - {res.task_id}')


ImportStocks.register()
