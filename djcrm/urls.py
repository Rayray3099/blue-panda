from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, include, reverse
from leads.views import LandingPageView, SignupView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing-page'),
    path('agents/', include('agents.urls', namespace="agents")),
    path('dashboard/', include('dashboard.urls', namespace="dashboard")),
    path('leads/', include('leads.urls', namespace="leads")),
    path('products/', include('products.urls', namespace="products")),
    path('invoices/', include('invoices.urls', namespace="invoices")),
    path('quotes/', include('quotes.urls', namespace="quotes")),
    path('suppliers/', include('suppliers.urls', namespace="suppliers")),
    path('scheduler/', include('scheduler.urls', namespace="scheduler")),
    path('signup/', SignupView.as_view(), name='signup'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('password-reset-done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
