from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Electrician, OutageReport, User


class CitizenRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "address", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "form-control"})
            else:
                field.widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "citizen"
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.address = self.cleaned_data["address"]
        if commit:
            user.save()
        return user


class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "admin"
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        if commit:
            user.save()
        return user


class OutageReportForm(forms.ModelForm):
    class Meta:
        model = OutageReport
        fields = ["title", "description", "address", "latitude", "longitude", "priority"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Brief title for the outage", "class": "form-control"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Describe the outage in detail", "class": "form-control"}
            ),
            "address": forms.Textarea(attrs={"rows": 2, "placeholder": "Full address", "class": "form-control"}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
            "priority": forms.Select(attrs={"class": "form-control form-select"}),
        }


class ElectricianForm(forms.ModelForm):
    class Meta:
        model = Electrician
        fields = ["name", "phone", "employee_id", "current_latitude", "current_longitude"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "employee_id": forms.TextInput(attrs={"class": "form-control"}),
            "current_latitude": forms.HiddenInput(),
            "current_longitude": forms.HiddenInput(),
        }


class ElectricianRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    employee_id = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "employee_id", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "electrician"
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        if commit:
            user.save()
            Electrician.objects.create(
                user=user,
                name=user.username,
                phone=self.cleaned_data["phone"],
                employee_id=self.cleaned_data["employee_id"],
            )
        return user


class AssignElectricianForm(forms.Form):
    electrician = forms.ModelChoiceField(
        queryset=Electrician.objects.filter(is_available=True),
        empty_label="Select an electrician",
        widget=forms.Select(attrs={"class": "form-control form-select"}),
    )
    estimated_restoration = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        required=False,
    )


class UpdateStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=OutageReport.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control form-select"}),
    )
    estimated_restoration = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        required=False,
    )
