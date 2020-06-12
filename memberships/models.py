from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
import stripe

stripe.api_key=settings.STRIPE_SECRET_KEY


PLAN_CHOICES=(
    ('quaterly','quaterly'),
    ('half yearly','half'),
    ('yearly','yearly')
)
# Create your models here.
class Membership(models.Model):
    price= models.IntegerField(default= 10)
    stripe_plan_id = models.CharField(max_length= 50)
    membership_type= models.CharField(choices=PLAN_CHOICES, max_length=20)
    slug= models.SlugField()

    def __str__(self):
        return self.membership_type
    
class Client(models.Model):
    user= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id= models.CharField(max_length=150)
    membership= models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username
def post_save_client_create(sender,instance, created, *args, **kwargs):
    if created:
        Client.objects.get_or_create(user=instance)
    
    client_membership, created= Client.objects.get_or_create(user=instance)

    if client_membership.stripe_customer_id is None or client_membership.stripe_customer_id=='':
        new_customer_id=stripe.Customer.create(email=instance.email)
        client_membership.stripe_customer_id= new_customer_id['id']
        client_membership.save()

post_save.connect(post_save_client_create, sender=settings.AUTH_USER_MODEL)


class Subscription(models.Model):
    client_membership= models.ForeignKey(Client, on_delete=models.CASCADE)
    stripe_subscription_id= models.CharField(max_length=50)
    active= models.BooleanField(default=True)

    def __str__(self):
        return self.client_membership.user.username
