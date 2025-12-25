from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
    # Marketplace
    path('marketplace/', views.marketplace, name='marketplace'),
    
    # User rewards
    path('my-rewards/', views.my_rewards, name='user_rewards'),
    
    # Actions
    path('redeem/<int:voucher_id>/', views.redeem_voucher, name='redeem_voucher'),
]