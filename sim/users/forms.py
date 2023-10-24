from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django import forms
User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class UserSignIn(forms.Form):
    email = forms.EmailField(
        label="Login", 
        required=False,
        widget=forms.EmailInput(
            attrs={'placeholder': 'Matricula ou Email'}
        )
    )
    password = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Digite sua senha'}
        )
    )

class UserSignUp(forms.Form):
    name = forms.CharField(
        label="Nome",
        widget=forms.TextInput()
    )
    surname = forms.CharField(
        label="Sobrenome",
        widget=forms.TextInput()
    )
    registration = forms.IntegerField(
        label="Matrícula",
        widget=forms.NumberInput()
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput()
    )
    number = forms.IntegerField(
        label="Número de telefone",
        widget=forms.NumberInput()
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput()
    )