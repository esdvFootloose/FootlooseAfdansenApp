from django import forms
from templates import widgets
from .models import *
from django.contrib.auth.models import User
from .models import Heat, MissingBackNumber
from django.db.models import Max
from django.core.exceptions import ValidationError
from .utils import getSuggestedBackNumber

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person

        fields = [
            'FirstName',
            'Prefix',
            'LastName',
        ]

        widgets = {
            'FirstName' : widgets.MetroTextInput,
            'Prefix'    : widgets.MetroTextInput,
            'LastName'  : widgets.MetroTextInput,
        }

class PairForm(forms.ModelForm):
    class Meta:
        model = Pair

        fields = [
            'BackNumber',
            'LeadingRole',
            'FollowingRole',
            'Dances',
        ]

        widgets = {
            'BackNumber'    : widgets.MetroNumberInput,
            'LeadingRole'   : widgets.MetroSelect,
            'FollowingRole' : widgets.MetroSelect,
            'Dances'        : widgets.MetroSelectMultiple,
        }

    def clean(self):
        super().clean()

        if self.instance.DoesNotExist == Pair.DoesNotExist:
            suggestedbacknumber = getSuggestedBackNumber(self.instance, [m.Number for m in MissingBackNumber.objects.all()], cleaned_data=self.cleaned_data, greedy=True)
        else:
            suggestedbacknumber = getSuggestedBackNumber(self.instance, [m.Number for m in MissingBackNumber.objects.all()])
        try:
            if self.cleaned_data['BackNumber'] in [n.Number for n in MissingBackNumber.objects.all()]:
                raise ValidationError("This is a missing backnumber. Suggested number: {}"
                                  .format(suggestedbacknumber))
        except KeyError:
            raise ValidationError("No valid backnumber specified. Suggested number: {}".format(suggestedbacknumber))

        for p in Pair.objects.filter(BackNumber=self.cleaned_data['BackNumber']):
            if p.LeadingRole != self.cleaned_data['LeadingRole']:
                raise ValidationError("Backnumber should be unique for a leader. Suggested number: {}"
                                      .format(suggestedbacknumber))

        return self.cleaned_data

class RegisterJuryForm(forms.Form):
    FirstName = forms.CharField(max_length=255, widget=widgets.MetroTextInput)
    LastName = forms.CharField(max_length=255, widget=widgets.MetroTextInput)
    Email = forms.EmailField(max_length=255, widget=widgets.MetroTextInput)
    Dances = forms.ModelMultipleChoiceField(queryset=Dance.objects.all(), widget=widgets.MetroSelectMultiple)


class EditJuryForm(forms.Form):
    Jury = forms.ModelChoiceField(queryset=User.objects.all(), widget=widgets.MetroSelect)
    Dances = forms.ModelMultipleChoiceField(queryset=Dance.objects.all(), widget=widgets.MetroSelectMultiple, required=False)

    def save(self):
        cleaned_data = self.clean()

        if 'Dances' not in cleaned_data:
            cleaned_data['Dances'] = []

        for d in cleaned_data['Jury'].jury.all():
            if d not in cleaned_data['Dances']:
                d.Jury.remove(cleaned_data['Jury'])
                d.save()

        for d in cleaned_data['Dances']:
            d.Jury.add(cleaned_data['Jury'])
            d.save()

class DanceSubDanceCreateForm(forms.Form):
    Dance = forms.ModelChoiceField(queryset=Dance.objects.all(), label='Dance Category:', widget=widgets.MetroSelect)
    SubDance = forms.CharField(max_length=255, widget=widgets.MetroTextInput, label='Sub Dance Name:')

class CsvUpload(forms.Form):
    csvfile = forms.FileField(widget=widgets.MetroFileInput)

class ConfirmForm(forms.Form):
    confirm = forms.BooleanField(widget=widgets.MetroCheckBox)

class HeatModelForm(forms.ModelForm):

    def clean_Number(self):
        data = self.cleaned_data['Number']
        m = Heat.objects.filter(Dance=self.cleaned_data['Dance']).aggregate(Max('Number'))['Number__max']
        if m is None:
            return data
        else:
            if data <= m:
                return m + 1
            else:
                return data

    class Meta:
        model = Heat

        fields = [
            'Dance',
            'Number',
            'Persons'
        ]

        widgets = {
            'Dance' : widgets.MetroSelect,
            'Number' : widgets.MetroNumberInput,
            'Persons' : widgets.MetroSelectMultiple,
        }

        labels = {
            'Persons' : 'Initial Persons (optional)'
        }