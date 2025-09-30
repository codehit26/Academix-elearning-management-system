from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Country, State, District


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='student'
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional phone number'})
    )


    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Country"
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select State"
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select District"
    )
    skype_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional Skype ID'})
    )
    whatsapp_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional WhatsApp number'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 'phone',
                  'country', 'state', 'district', 'skype_id', 'whatsapp_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        for field_name, field in self.fields.items():
            if field_name not in ['username', 'email', 'phone', 'skype_id', 'whatsapp_number']:
                field.widget.attrs.update({'class': 'form-control'})


        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })


        if self.data:
            country_id = self.data.get('country')
            state_id = self.data.get('state')
        else:
            country_id = None
            state_id = None


        if country_id:
            self.fields['state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
        else:
            self.fields['state'].queryset = State.objects.none()


        if state_id:
            self.fields['district'].queryset = District.objects.filter(state_id=state_id).order_by('name')
        else:
            self.fields['district'].queryset = District.objects.none()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone',
            'country', 'state', 'district', 'skype_id', 'whatsapp_number'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        if self.data:
            country_id = self.data.get('country')
            state_id = self.data.get('state')
        elif self.instance.pk:

            country_id = self.instance.country_id
            state_id = self.instance.state_id
        else:
            country_id = None
            state_id = None


        if country_id:
            self.fields['state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
        else:
            self.fields['state'].queryset = State.objects.none()


        if state_id:
            self.fields['district'].queryset = District.objects.filter(state_id=state_id).order_by('name')
        else:
            self.fields['district'].queryset = District.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data