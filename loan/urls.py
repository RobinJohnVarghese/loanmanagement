from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanViewSet, AdminLoanViewSet,ForecloseLoanViewSet

router = DefaultRouter()
router.register('loans', LoanViewSet, basename='loan')
router.register('admin/loans', AdminLoanViewSet, basename='admin-loan')
# router.register(r'loans/(?P<loan_id>[^/.]+)/foreclose', ForecloseLoanViewSet, basename='foreclose-loan')
# router.register('foreclose-loans/', ForecloseLoanViewSet, basename='foreclose-loan'),

# Register foreclosure API
foreclose_router = DefaultRouter()
foreclose_router.register(r'foreclose-loans', ForecloseLoanViewSet, basename='foreclose-loan')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(foreclose_router.urls)),
    # path('loans/<loan_id>/foreclose/', ForecloseLoanView.as_view(), name='foreclose-loan'),
]
