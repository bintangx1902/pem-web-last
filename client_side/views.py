from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from django.db.models import Q as __
from .forms import *
from .utils import *
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_id = ""


def landing(request):
    form = JoinUsForms()
    return render(request, get_template('landing'), {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def check_user_level(request):
    if request.user.is_staff or (request.user.user.is_employee if hasattr(request.user, 'user') else False):
        return redirect(reverse('comp:landing'))
    return redirect(reverse('comp:landing'))


class JoinUsView(View):
    def get(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, *args, **kwargs):
        form = JoinUsForms(self.request.POST or None, self.request.FILES or None)
        if form.is_valid():
            form.instance.user = self.request.user
            form.save()
        return redirect('/')

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        return super(JoinUsView, self).dispatch(request, *args, **kwargs)


class CreateComplaint(CreateView):
    model = Complaint
    form_class = CreateComplaintForm
    template_name = get_template('create_complaint')

    def get_success_url(self):
        return reverse('client:my-complaint-list')

    def form_valid(self, form):
        form.instance.complain = self.request.user
        form.instance.ticket_code = get_ticket_code()
        return super().form_valid(form)

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        data = True if hasattr(self.request.user, 'user') else False
        if not data:
            # lengkapi data anda
            return redirect('client:profile')
        return super(CreateComplaint, self).dispatch(request, *args, **kwargs)


class MyComplaintList(ListView):
    model = Complaint
    context_object_name = 'items'
    template_name = get_template('list_complaint')
    paginate_by = 5

    def get_queryset(self):
        q = self.request.GET.get('q')
        query = self.model.objects.filter(complain=self.request.user) if not q else \
            self.model.objects.filter(__(title__icontains=q) | __(messages__icontains=q)).filter(
                complain=self.request.user)
        return query.order_by('-created')

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_active and (u.user.nik is not None if hasattr(u, 'user') else False),
                         '/accounts/profile'))
    def dispatch(self, request, *args, **kwargs):
        return super(MyComplaintList, self).dispatch(request, *args, **kwargs)


class MyComplaint(DetailView):
    model = Complaint
    slug_url_kwarg = 'ticket_code'
    slug_field = 'ticket_code'
    query_pk_and_slug = True
    context_object_name = 'com'
    template_name = get_template('complaint_detail')

    def get_context_data(self, **kwargs):
        context = super(MyComplaint, self).get_context_data(**kwargs)
        context['public_key'] = settings.STRIPE_PUBLIC_KEY
        context['der'] = list(range(10))
        return context

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_active and (u.user.nik is not None if hasattr(u, 'user') else False),
                         '/accounts/profile'))
    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Complaint, ticket_code=self.kwargs['ticket_code'])
        if not instance.complain == self.request.user:
            return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super(MyComplaint, self).dispatch(request, *args, **kwargs)


""" Profile added """


class ProfileView(View):
    def get(self, *args, **kwargs):
        instance = UserProfile.objects.get(user=self.request.user) if hasattr(self.request.user, 'user') else None
        u_form = UserProfileForm(instance=instance)
        form = UserForm(instance=self.request.user)
        context = {
            'form': form,
            'u_form': u_form
        }
        return render(self.request, get_template('profile'), context)

    def post(self, *args, **kwargs):
        instance = UserProfile.objects.get(user=self.request.user) if hasattr(self.request.user, 'user') else None
        form = UserForm(self.request.POST or None, instance=self.request.user)
        u_form = UserProfileForm(self.request.POST or None, instance=instance)
        if form.is_valid() and u_form.is_valid():
            form.save()
            u_form.instance.user = self.request.user
            u_form.save()
        else:
            messages.warning(self.request, 'Data tidak Lengkap!')

        return redirect('client:profile') if not self.request.GET.get('next') else redirect(
            self.request.GET.get('next'))

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileView, self).dispatch(request, *args, **kwargs)


""" Checkout """


class CheckoutView(View):
    def get(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, *args, **kwargs):
        global stripe_id
        host = self.request.get_host()
        item = get_object_or_404(Complaint, ticket_code=kwargs['ticket_code'])
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'idr',
                        'unit_amount': item.total_price * 100,  # amount * usd_cents,
                        'product_data': {
                            'name': f"Billing for ticket {item.ticket_code}",
                            'images': ['https://i.imgur.com/W1bWtgl.jpeg']
                        }
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f"http://{host}{reverse('client:payment-success', kwargs={'ticket_code': item.ticket_code})}",
            cancel_url=f"http://{host}{reverse('client:payment-cancel', kwargs={'ticket_code': item.ticket_code})}"
        )
        # return JsonResponse({
        #     'id': checkout_session.id
        # })

        stripe_id = checkout_session.id
        return redirect(checkout_session.url, code=302)


class PaymentSuccessView(View):
    def get(self, *args, **kwargs):
        global stripe_id
        item = get_object_or_404(Complaint, ticket_code=kwargs['ticket_code'])
        item.stripe_id = stripe_id
        stripe_id = ''
        item.is_success = True
        item.save()
        return render(self.request, get_template('payment-success'))

    def post(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        return super(PaymentSuccessView, self).dispatch(request, *args, **kwargs)


class CancelPaymentView(View):
    def get(self, *args, **kwargs):
        global stripe_id
        item = get_object_or_404(Complaint, ticket_code=kwargs['ticket_code'])
        item.stripe_id = stripe_id
        stripe_id = ''
        item.is_success = False

        item.save()
        return render(self.request, get_template('payment-cancel'))

    def post(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        return super(CancelPaymentView, self).dispatch(request, *args, **kwargs)
