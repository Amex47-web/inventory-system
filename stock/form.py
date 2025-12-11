from django import forms
from .models import *

class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        # CHANGED: Added 're_order' so it appears on the Add Stock page
        fields = ['category', 'item_name', 'quantity','unit_price', 're_order','supplier', 'image', 'date']

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('This field is required')
        return category

    def clean_item_name(self):
        item_name = self.cleaned_data.get('item_name')
        if not item_name:
            raise forms.ValidationError('This field is required')
        return item_name


class StockHistorySearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)

    class Meta:
        model = StockHistory
        fields = ['category', 'item_name', 'start_date', 'end_date']


class StockSearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)

    class Meta:
        model = Stock
        fields = ['category', 'item_name']


class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        # CHANGED: Added 're_order' and 'date' so you can edit them later
        fields = ['category', 'item_name', 'quantity','unit_price', 're_order', 'supplier', 'image', 'date']


class IssueForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['issue_quantity', 'issued_to']


class ReceiveForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['receive_quantity']


class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['re_order']


class DependentDropdownForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['state'].queryset = State.objects.none()
        if 'country' in self.data:
            try:
                country_idm = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_idm).order_by('name')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['state'].queryset = self.instance.country.state_set.order_by('name')

        self.fields['city'].queryset = City.objects.none()
        if 'state' in self.data:
            try:
                state_idm = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_idm).order_by('name')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.state.city_set.order_by('name')


class AddScrumListForm(forms.ModelForm):
    class Meta:
        model = ScrumTitles
        fields = ['lists']


class AddScrumTaskForm(forms.ModelForm):
    class Meta:
        model = Scrums
        fields = ['task', 'task_description', 'task_date']


class ContactsForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = '__all__'