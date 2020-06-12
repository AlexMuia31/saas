from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import ListView
from django.contrib import messages
from .models import Membership, Client, Subscription
from django.http import HttpResponseRedirect
from django.urls import reverse
import stripe


def get_client_membership(request):
    client_membership_qs= Client.objects.filter(user=request.user)
    if client_membership_qs.exists():
        return client_membership_qs.first()
    return None

def get_user_subscription(request):
    client_subscription_qs= Subscription.objects.filter(
        client_membership= get_client_membership(request))
    if client_subscription_qs.exists():
        client_subscription= client_subscription_qs.first()
        return client_subscription
    return None

def get_selected_membership(request):
    membership_type=request.session['selected_membership_type']
    selected_membership_qs=Membership.objects.filter(membership_type=membership_type)
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None


class MembershipSelectView(ListView):
    model= Membership
    
    def get_context_data(self, *args , **kwargs):
        context= super().get_context_data(**kwargs)
        current_membership=get_client_membership(self.request)
        context['current_membership']= str(current_membership.membership)
        return context
    
    def post(self, request, **kwargs):
        selected_membership_type = request.POST.get('membership_type')
        client_membership= get_client_membership(request)
        client_subscription= get_user_subscription(request)
        
        selected_membership_qs= Membership.objects.filter(membership_type=selected_membership_type)

        if selected_membership_qs.exists():
            selected_membership=selected_membership_qs.first()

        if client_membership.membership==selected_membership:
            if client_subscription != None:
                messages.info(request,"You already have this membership.Your next paymentis due {}",format('get this value from stripe'))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        request.session['selected_membership_type']= selected_membership.membership_type
        return HttpResponseRedirect(reverse('memberships:payment'))

def PaymentView(request):
    client_membership= get_client_membership(request)
    selected_membership= get_selected_membership(request)

    publishKey=settings.STRIPE_PUBLISHABLE_KEY

    if request.method=='POST':
        try:
            token= request.POST['stripeToken']
            customer = stripe.Customer.retrieve(client_membership.stripe_customer_id)
            customer.source = token # 4242424242424242
            customer.save()


            subscription= stripe.Subscription.create(
                customer='client_membership.stripe_customer_id',
                items=[{
                    'plan':selected_membership.stripe_plan_id,
                }]
                
                
            )
            return redirect(reverse('memberships:update-transactions', 
            kwargs={
                'subscription_id': subscription.id
            }))

        except stripe.error.CardError:
            messages.info(request,'Your card has been declined')

    context={
        'publishKey': publishKey,
        'selected_membership': selected_membership
    }
    return render(request,'memberships/membership_payment.html', context)

def updateTransactions(request, subscription_id):
    client_membership= get_client_membership(request)

    selected_membership= get_selected_membership(request)

    client_membership.membership= selected_membership
    client_membership.save()
    
    sub, created= Subscription.objects.get_or_create(client_membership=client_membership)
    sub.stripe_subscription_id = subscription_id
    sub.active= True
    sub.save()

    try:
        del request.session['selected_membership_type']
    except:
        pass
    messages.info(request,'successfully created {} membership'.format(selected_membership))
    return redirect('/courses')

