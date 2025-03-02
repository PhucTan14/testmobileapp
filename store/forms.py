from allauth.account.forms import SignupForm
from django import forms

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='Tên')
    last_name = forms.CharField(max_length=30, label='Họ')
    phone = forms.CharField(max_length=15, label='Số điện thoại', required=False)
    address = forms.CharField(max_length=255, label='Địa chỉ', required=False)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.save()
        return user
    
