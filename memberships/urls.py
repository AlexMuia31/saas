from django.urls import path
from memberships.views import MembershipSelectView, PaymentView, updateTransactions

app_name= 'memberships'
urlpatterns = [
    path('',MembershipSelectView.as_view(), name='select'),
    path('payment/',PaymentView, name='payment'),
    path('update-transactions<subscription_id>/', updateTransactions, name='update-transactions')
]