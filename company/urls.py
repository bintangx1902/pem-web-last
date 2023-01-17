from .views import *
from django.urls import path

app_name = 'comp'

urlpatterns = [
    path('', CompanyLanding.as_view(), name='landing'),
    path('applicant', ApplicantListView.as_view(), name='applicant-list'),
    path('applicant/<code>', ApplicantDetailView.as_view(), name='applicant-detail'),
    path('applicant/<code>/<target>', AcceptOrReject.as_view(), name='accept-reject'),
    path('complaint', ComplaintList.as_view(), name='unacc-complaint'),
    path('complaint/ticket_<ticket_code>', ComplaintDetail.as_view(), name='complaint-detail'),
    path('complaint/ticket_<ticket_code>/acc', accept_ticket, name='accept-ticket'),
    path('complaint/ticket_<ticket_code>/reject', reject_ticket, name='reject-ticket'),
    path('complaint/ticket_<ticket_code>/open', OpenJob.as_view(), name='open-job'),
    path('complaint/ticket_<ticket_code>/close', CloseThisComplaint.as_view(), name='close-complaint'),
]

urlpatterns.extend([
    path('complaint/job', JobListForTechnician.as_view(), name='job-list'),
    path('complaint/job/mine', SeeMyJob.as_view(), name='all-my-job'),
    path('complaint/job/<ticket_code>', OpenComplaintDetail.as_view(), name='job-detail'),
    path('complaint/job/<ticket_code>/take', GetThisJob.as_view(), name='take-this-job'),
    path('complaint/job/<ticket_code>/report', GroundReportView.as_view(), name='ground-report'),
    path('complaint/job/<ticket_code>/set-price', SetGroundPriceView.as_view(), name='set-ground-price'),
])
