from datetime import date

from django import forms
from .models import Projects, Tasks, Comments, Customers


class ProjectForm(forms.ModelForm):
    deadline = forms.DateInput()

    class Meta:
        model = Projects
        fields = ('name', 'customer_id', 'description', 'deadline', 'status', 'curator', 'budget')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'modal_title_form'}),
            'customer_id': forms.Select(attrs={'class': 'modal_customer_form'}),
            'status': forms.Select(attrs={'class': 'modal_status_form', 'id': "status_field"}),
            'description': forms.Textarea(attrs={'class': 'modal_desc_form'}),
            'curator': forms.Select(attrs={'class': 'modal_curator_form', 'id': "curator_field"}),
            'budget': forms.NumberInput(attrs={'class': 'modal_budget_form'}),
            'deadline': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'modal_deadline_form',
                                                                  'type': 'date',
                                                                  'min': date.today})
        }


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customers
        fields = ('name', 'director', 'phone', 'email', 'inn', 'kpp', 'bill_acc', 'bik')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'modal_title_form'}),
            'director': forms.TextInput(attrs={'class': 'modal_title_form'}),
            'phone': forms.TextInput(attrs={'class': 'modal_status_form', 'type': 'phone'}),
            'email': forms.TextInput(attrs={'class': 'modal_desc_form', 'type': 'email'}),
            'inn': forms.TextInput(attrs={'class': 'modal_status_form'}),
            'kpp': forms.TextInput(attrs={'class': 'modal_desc_form'}),
            'bill_acc': forms.TextInput(attrs={'class': 'modal_status_form'}),
            'bik': forms.TextInput(attrs={'class': 'modal_desc_form'}),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('project_id', 'emp_id', 'comment')
        widgets = {
            'project_id': forms.Select(),
            'emp_id': forms.Select(),
            'comment': forms.TextInput(attrs={'class': 'com_input'}),
        }
