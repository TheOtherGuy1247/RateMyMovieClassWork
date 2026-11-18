from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """
    Django's built-in sign-up form (username + password twice, with all of
    Django's password checks), plus a required email address.
    Saves a normal Django User.
    """

    email = forms.EmailField(
        required=True,
        help_text="We'll only use it if you forget your password.",
    )

    class Meta:
        model = User
        fields = ["username", "email"] # password1 and password2 come from UserCreationForm

    def clean_email(self):
        """One account per email address, ignoring upper/lower case."""
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email
    