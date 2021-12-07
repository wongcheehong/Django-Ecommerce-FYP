from django import forms
from .models import User, Profile
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'username',
            'email',
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'password1',
            'password2',
        )


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'email',
        )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo',)
        widgets = {
            'photo': forms.FileInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('photo', ),

            ),
            Div(
                Submit('submit', 'Save', css_class='btn btn-danger btn-lg'),
                css_class='d-flex justify-content-center'
            ),
        )







STATE_CHOICES = (
    ('Selangor', 'Selangor'),
    ('Kuala Lumpur', 'Kuala Lumpur'),
    ('Johor', 'Johor'),
    ('Sarawak', 'Sarawak'),
    ('Sabah', 'Sabah'),
    ('Perak', 'Perak'),
    ('Penang', 'Penang'),
    ('Kedah', 'Kedah'),
    ('Pahang', 'Pahang'),
    ('Negeri Sembilan', 'Negeri Sembilan'),
    ('Kelantan', 'Kelantan'),
    ('Terengganu', 'Terengganu'),
    ('Melaka', 'Melaka'),
    ('Putrajaya', 'Putrajaya'),
    ('Perlis', 'Perlis'),
    ('Labuan', 'Labuan'),
)


class AddressForm(forms.Form):
    # Address detail
    address_name = forms.CharField(required=True, max_length=100)
    address = forms.CharField(required=True, max_length=100)
    address_state = forms.ChoiceField(required=True, choices=STATE_CHOICES, label="State")
    address_city = forms.CharField(required=True, max_length=30)
    address_zip = forms.CharField(required=True, max_length=5, widget=forms.TextInput(attrs={'type': 'number'}))