from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts import views 


router = DefaultRouter()

router.register(r'users', views.UserViewSet, basename='user')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'beneficiaries', views.BeneficiaryViewSet, basename='beneficiary')


urlpatterns = [
    path('api/accounts/', include(router.urls)),
    path('auth/register/', views.RegisterUserView.as_view(), name='register'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

]