from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import FormView
from ..core.views import ListView, TableListView, CreateView, DetailView
from .models import Lending, Return
from django.views.generic import View
from django.utils import timezone
from datetime import timedelta
from .tables import LendingTable
from django_tables2 import SingleTableView
from .tables import LendingFilter, ReturnFilter, LendingStudentFilter
from ..instruments.models import Instrument
from .forms import LendingForm, ReturnForm
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
# Create your views here.

from django_filters.views import FilterView

    
class LendingListView(FilterView, ListView):
    model = Lending
    template_name = "lendings/lendings_in_progress.html"
    paginate_by = 10
    filterset_class = LendingFilter
    
    def get_queryset(self):
        queryset = Lending.objects.filter(status=Lending.StatusChoices.IN_PROGRESS).order_by("created_at")

        return queryset



class LendingRequestsListView(FilterView, ListView):
    model = Lending
    template_name = "lendings/solicitations_list.html"
    paginate_by = 10
    filterset_class = LendingFilter

    def get_queryset(self) -> QuerySet[Any]:
        query = Lending.objects.filter(status=Lending.StatusChoices.IN_ANALISYS).order_by("created_at")

        return query

class LendingStudentListView(FilterView, ListView):
    model = Lending
    template_name = "lendings/student_requests.html"
    paginate_by = 10
    filterset_class = LendingStudentFilter

    def get_queryset(self) -> QuerySet[Any]:
        query = Lending.objects.filter(student=self.request.user.StudentUser).order_by("created_at")

        return query
    


class LendingCreateView(CreateView):
    model = Lending
    template_name = "lendings/form.html"
    success_url = "/instruments/list/"
    form_class = LendingForm

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        student = self.request.user.StudentUser
        lendings = Lending.objects.filter(student=student)
        can_create = True


        if student.has_penalty == True:

            if student.penalty_end < timezone.now().date():
                student.penalty_end = None
                student.has_penalty = False
            else:
                messages.error(self.request, "Não foi possível solicitar o empréstimo pois você ainda possui um penalidade aplicada")
                return redirect(self.success_url)

        for l in lendings:
            if l.active == True:
                can_create = False

        if can_create:
            lending = form.save(commit=False)
            lending.student = student
            instrument = Instrument.objects.get(pk=self.kwargs['pk'])
            instrument.status = False
            instrument.save()
            lending.instrument = instrument

            lending.save()
            messages.success(self.request, "Solicitação de empréstimo criado com sucesso")
            return redirect(self.success_url)
        else:
            messages.warning(self.request, "Não foi possível solicitar o empréstimo pois você ainda possui um solicitação em aberto")
            return redirect(self.success_url)


class ReturnCreateView(PermissionRequiredMixin, CreateView):
    model = Return
    template_name = "lendings/return_form.html"
    success_url = "/lendings/list/"
    form_class = ReturnForm
    permission_required = "lendings.add_return"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        return_form = form.save(commit=False)
        lending = Lending.objects.get(pk=self.kwargs['pk'])
        return_form.lending = lending
        student = lending.student

        lending.status = lending.StatusChoices.FINISHED
        lending.active = False

        instrument = lending.instrument
        instrument.status = True

        if lending.finalDate < timezone.now().date():
            student.has_penalty = True
            student.penalty_end = timezone.now().date() + timedelta(days=7)

        lending.save()
        instrument.save()
        return_form.save()
        student.save()
        messages.success(self.request, "Devolução criada com sucesso")
        return redirect(self.success_url)
    


class LendingDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "lendings.add_return"
    model = Lending
    template_name = "lendings/lending_detail.html"


class LendingAnalysisView(PermissionRequiredMixin, DetailView):
    model = Lending
    template_name = "lendings/lending_request_detail.html"
    permission_required = "lendings.add_return"

class ReturnsListView(PermissionRequiredMixin, FilterView, ListView):
    model = Return
    template_name = "lendings/returns_list.html"
    paginate_by = 10
    filterset_class = ReturnFilter
    permission_required = "lendings.add_return"

class DeniedView(PermissionRequiredMixin, View):
    permission_required = "lendings.add_return"

    def get(self, request, *args, **kwargs):
        lending = Lending.objects.get(pk=self.kwargs['pk'])
        
        lending.status = lending.StatusChoices.DENIED
        lending.active = False
        lending.responsible = self.request.user

        instrument = lending.instrument
        instrument.status = True

        instrument.save()
        lending.save()
        messages.success(self.request, "Solicitação indeferida com sucesso")
        return redirect("/lendings/requests/")

class AcceptView(PermissionRequiredMixin, View):
    permission_required = "lendings.add_return"

    def get(self, request, *args, **kwargs):
        lending = Lending.objects.get(pk=self.kwargs['pk'])

        if lending.student.user.groups.filter(name="colleger").exists():
            messages.warning(self.request, "Um solicitação de bolsista só pode ser aceita por professores")
            return redirect("/lendings/requests/")

        lending.status = lending.StatusChoices.IN_PROGRESS
        lending.active = True
        lending.responsible = self.request.user

        instrument = lending.instrument
        instrument.status = False

        instrument.save()
        lending.save()
        messages.success(self.request, "Solicitação deferida com sucesso")
        return redirect("/lendings/requests/")
    

class CancelView(View):
    
    def get(self, request, *args, **kwargs):
        lending = Lending.objects.get(pk=self.kwargs['pk'])
        
        lending.status = lending.StatusChoices.CANCELED
        lending.active = False

        instrument = lending.instrument
        instrument.status = True

        instrument.save()
        lending.save()
        messages.success(self.request, "Solicitação cancelada com sucesso")
        return redirect("/lendings/requests/")