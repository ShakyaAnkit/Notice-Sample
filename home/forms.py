from dateutil import parser

from django import forms

from dashboard.models import Ministry, Office

from nepali.datetime import NepaliDate

class FilterForm(forms.Form):
    search = forms.CharField(required=False)
    ministry = forms.ModelChoiceField(queryset=Ministry.objects.all(), required=False)
    # office = forms.ModelChoiceField(queryset=Office.objects.all(), required=False)
    start_date = forms.CharField(required=False)
    end_date = forms.CharField(required=False)


    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        
        if start_date == None or start_date == '':
            return None

        try:
            return NepaliDate(*[int(i) for i in start_date.split('-') ]).to_date()
        except:
            raise forms.ValidationError(
                'Invalid start date'
            )

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')

        if end_date == None or end_date == '':
            return None

        try:
            return NepaliDate(*[int(i) for i in end_date.split('-') ]).to_date()
        except:
            raise forms.ValidationError(
                'Invalid end date'
            )


    def clean_search(self):
        search = self.cleaned_data.get('search')

        if search == None or search == '':
            return None
        
        return search
    
    def clean_ministry(self):
        ministry = self.cleaned_data.get('ministry')

        if ministry == None or ministry == '':
            return None
        
        return ministry

    # def clean_office(self):
    #     office = self.cleaned_data.get('office')

    #     if office == None or office == '':
    #         return None
        
    #     return office

    def is_filtered(self):
        if self.cleaned_data.get('search') != None and self.cleaned_data.get('search')!= '':
            return True
        elif self.cleaned_data.get('ministry')!= None and self.cleaned_data.get('ministry')!= '':
            return True
        elif self.cleaned_data.get('office')!= None and self.cleaned_data.get('office')!= '':
            return True
        elif self.cleaned_data.get('start_date')!= None and self.cleaned_data.get('start_date')!= '':
            return True
        elif self.cleaned_data.get('end_date')!= None and self.cleaned_data.get('end_date')!= '':
            return True
        else:
            return False