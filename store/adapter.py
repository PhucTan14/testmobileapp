from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from store.models import User
from django.shortcuts import redirect
from django.contrib import messages
from allauth.core.exceptions import ImmediateHttpResponse

class NoSignupAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True
    
    


class NoSignupSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
       if not sociallogin.is_existing:
            user = User.objects.filter(email=sociallogin.account.extra_data['email']).first()
            if user:
                messages.error(request, "Email đã tồn tại. Vui lòng đăng nhập bằng tên người dùng và mật khẩu của bạn.")
                raise ImmediateHttpResponse(redirect('account_login'))
            
            user = sociallogin.user
            user.email = sociallogin.account.extra_data['email']
            user.first_name = sociallogin.account.extra_data.get('given_name', '')
            user.last_name = sociallogin.account.extra_data.get('family_name', '')
            # user.username = sociallogin.account.extra_data['email']
            user.avatar_url = sociallogin.account.extra_data.get('picture', '')
            user.save()
            sociallogin.connect(request, user)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.emailaddress_set.create(
            user=user,
            email=user.email,
            verified=True,
            primary=True
        )
        return user