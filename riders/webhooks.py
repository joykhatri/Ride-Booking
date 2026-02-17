from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe
from django.conf import settings
from riders.models import RiderPayment
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def webhook(request):
    payload = request.body
    endpoint_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)

    if endpoint_secret:
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            print('Webhook signature verification failed.', e)
            return HttpResponse(status=400)
    else:
        event=json.loads(payload)
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        stripe_id = payment_intent['id']

        RiderPayment.objects.filter(stripe_payment_intent=stripe_id).update(paid=True)
        print(f'Payment succeeded for PaymentIntent {stripe_id}')

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        stripe_id = payment_intent['id']

        RiderPayment.objects.filter(stripe_payment_intent=stripe_id).update(paid=False)
        print(f'Payment failed for PaymentIntent {stripe_id}')

    else:
        print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(status=200)

