from rest_framework import status

from .utils import *
from .forms import *
from django.views.generic import *
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages


class CompanyLanding(TemplateView):
    template_name = get_template('landing')

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/',
                         redirect_field_name=None))
    def dispatch(self, request, *args, **kwargs):
        return super(CompanyLanding, self).dispatch(request, *args, **kwargs)


class ComplaintList(ListView):
    model = Complaint
    context_object_name = 'items'
    template_name = get_template('list_complaint')
    paginate_by = 2

    def get_queryset(self):
        acc = self.request.GET.get('acc')
        user = self.request.user

        query = self.model.objects.filter(is_done=False, accepted=False) if not acc else self.model.objects.filter(
            is_done=False, accepted=True, cs=user)
        return query.order_by('-id')

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(ComplaintList, self).dispatch(request, *args, **kwargs)


class ComplaintDetail(DetailView):
    model = Complaint
    template_name = get_template('complaint_detail')
    query_pk_and_slug = True
    slug_url_kwarg = 'ticket_code'
    slug_field = 'ticket_code'
    context_object_name = 'com'

    def get_context_data(self, **kwargs):
        context = super(ComplaintDetail, self).get_context_data(**kwargs)
        proof = GroundReport.objects.filter(job__ticket_code=self.kwargs['ticket_code'])
        form = OpenJobForm()

        context['proof'] = proof
        context['form'] = form
        return context

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(ComplaintDetail, self).dispatch(request, *args, **kwargs)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/')
def accept_ticket(request, ticket_code):
    ticket = get_object_or_404(Complaint, ticket_code=ticket_code)
    ticket.accepted = True
    ticket.is_done = False
    ticket.rejected = False
    ticket.is_open = False
    ticket.cs = request.user
    ticket.save()
    return redirect(reverse('comp:complaint-detail', kwargs={'ticket_code': ticket_code}))


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/')
def reject_ticket(request, ticket_code):
    ticket = get_object_or_404(Complaint, ticket_code=ticket_code)
    ticket.accepted = False
    ticket.is_done = False
    ticket.rejected = True
    ticket.save()
    return redirect(reverse('comp:complaint-detail', kwargs={'ticket_code': ticket_code}))


class OpenJob(View):
    def get(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, *args, **kwargs):
        ticket = get_object_or_404(Complaint, ticket_code=self.kwargs.get('ticket_code'))
        form = OpenJobForm(self.request.POST or None, self.request.FILES or None, instance=ticket)
        if form.is_valid():
            form.instance.is_open = True
            form.save()
        return redirect(reverse('comp:complaint-detail', kwargs={'ticket_code': ticket.ticket_code}))

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(OpenJob, self).dispatch(request, *args, **kwargs)


class CloseThisComplaint(View):
    def get(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, *args, **kwargs):
        complaint = get_object_or_404(Complaint, ticket_code=self.kwargs['ticket_code'])
        tech_price = complaint.tech_price * len(complaint.job.all())
        complaint.total_price = complaint.ground_price + complaint.stock_price + tech_price
        complaint.is_done = True
        complaint.save()
        return redirect(reverse('comp:complaint-detail', args=[self.kwargs['ticket_code']]))

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(CloseThisComplaint, self).dispatch(request, *args, **kwargs)


class ApplicantListView(ListView):
    model = JoinUs
    template_name = get_template('applicant_list')
    context_object_name = 'items'

    def get_queryset(self):
        return self.model.objects.filter(accepted=False)


class ApplicantDetailView(DetailView):
    model = JoinUs
    context_object_name = 'app'
    template_name = get_template('applicant_detail')
    slug_url_kwarg = 'code'
    slug_field = 'code'

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(ApplicantDetailView, self).dispatch(request, *args, **kwargs)


class AcceptOrReject(View):
    def get(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, *args, **kwargs):
        applicant = get_object_or_404(JoinUs, code=kwargs['code'])
        target = kwargs['target']
        if target == 1:
            pass
        elif not target:
            pass
        else:
            return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(AcceptOrReject, self).dispatch(request, *args, **kwargs)


""" below this segment is for the technician """


class GetThisJob(View):

    def get(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, *args, **kwargs):
        ticket = get_object_or_404(Complaint, ticket_code=self.kwargs.get('ticket_code'))
        instance = TechnicianJob.objects.filter(job=ticket, user=self.request.user)
        if not instance:
            instance = TechnicianJob(
                user=self.request.user,
                job=ticket
            )
            instance.save()
            ticket.tech_quota -= 1
            if ticket.tech_quota <= 0:
                ticket.is_open = False
                ticket.tech_quota = 0
            ticket.save()

        else:
            messages.warning(self.request, 'kamu sudah mengambil pekerjaan ini')

        return redirect(reverse('comp:job-detail', kwargs={'ticket_code': ticket.ticket_code}))

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(GetThisJob, self).dispatch(request, *args, **kwargs)


class JobListForTechnician(ListView):
    template_name = get_tech_template('open_job_list')
    context_object_name = 'items'
    model = Complaint

    def get_queryset(self):
        return self.model.objects.filter(is_done=False, accepted=True, is_open=True)

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(JobListForTechnician, self).dispatch(request, *args, **kwargs)


class OpenComplaintDetail(DetailView):
    model = Complaint
    template_name = get_tech_template('complaint_detail')
    query_pk_and_slug = True
    slug_field = 'ticket_code'
    slug_url_kwarg = 'ticket_code'
    context_object_name = 'com'

    def get_context_data(self, **kwargs):
        context = super(OpenComplaintDetail, self).get_context_data(**kwargs)
        query = TechnicianJob.objects.filter(job__ticket_code=self.kwargs['ticket_code'], user=self.request.user)
        form = GroundReportForm()
        report = GroundReport.objects.filter(job__ticket_code=self.kwargs['ticket_code'])
        ground_price = SetGroundPriceForm(instance=self.object)

        context['work'] = True if query else False
        context['form'] = form
        context['report'] = report
        context['ground_price'] = ground_price
        return context

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(OpenComplaintDetail, self).dispatch(request, *args, **kwargs)


class SeeMyJob(ListView):
    model = TechnicianJob
    context_object_name = 'items'
    template_name = get_tech_template('list_complaint')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user, job__is_done=False)

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(SeeMyJob, self).dispatch(request, *args, **kwargs)


class GroundReportView(View):
    model = GroundReport
    form_class = GroundReportForm

    def get(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST or None, self.request.FILES or None)
        if form.is_valid():
            form.instance.user = self.request.user
            form.instance.job = get_object_or_404(Complaint, ticket_code=self.kwargs.get('ticket_code'))
            form.save()
        return redirect(reverse('comp:job-detail', kwargs={'ticket_code': self.kwargs.get('ticket_code')}))

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(GroundReportView, self).dispatch(request, *args, **kwargs)


class SetGroundPriceView(View):
    def get(self, *args, **kwargs):
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, *args, **kwargs):
        instance = get_object_or_404(Complaint, ticket_code=self.kwargs['ticket_code'])
        form = SetGroundPriceForm(self.request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
        return redirect(reverse('comp:job-detail', args=[self.kwargs['ticket_code']]))

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    @method_decorator(
        user_passes_test(lambda u: u.is_staff or (u.user.is_employee if hasattr(u, 'user') else False), '/'))
    def dispatch(self, request, *args, **kwargs):
        return super(SetGroundPriceView, self).dispatch(request, *args, **kwargs)
