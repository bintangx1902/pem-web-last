from django.urls import path
from .views import *

app_name = 'client'

urlpatterns = [
    path('', landing, name='landing'),
    path('join-us', JoinUsView.as_view(), name='join-us'),
    path('check', check_user_level, name='check'),
    path('complaint', CreateComplaint.as_view(), name='create-complaint'),
    path('complaint/mine', MyComplaintList.as_view(), name='my-complaint-list'),
    path('complaint/mine/<ticket_code>', MyComplaint.as_view(), name='my-complaint'),
    path('complaint/mine/<ticket_code>/payment', CheckoutView.as_view(), name='pay-complaint'),
]

urlpatterns.extend([
    path('complaint/<ticket_code>/payment/success', PaymentSuccessView.as_view(), name='payment-success'),
    path('complaint/<ticket_code>/payment/cancel', CancelPaymentView.as_view(), name='payment-cancel'),
])

urlpatterns.extend([
    path('accounts/profile', ProfileView.as_view(), name='profile'),
])
