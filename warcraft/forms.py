from django import forms
from warcraft.models import User

class FriendsForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput)
    class Meta:
        fields = ('name')



class RegistrationForm(forms.ModelForm):
        userName = forms.CharField(widget=forms.TextInput, label="Username")
        password1 = forms.CharField(widget=forms.PasswordInput,
                                label="Password")
        password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Password (again)")

        firstName = forms.CharField(widget=forms.TextInput,label="FirstName")
        lastName = forms.CharField(widget=forms.TextInput,label="LastName")
        email = forms.EmailField(widget=forms.TextInput,label="Email")
        CHOICES=[(0,'Immediate'),
         (10,'Every 10 minutes'), (60, 'Every hour')]
        emailEvery = forms.ChoiceField(label='Notification Frequency', choices=CHOICES)
        class Meta:
                model = User
                fields = ['firstName', 'lastName', 'userName', 'email', 'password1', 'password2', 'picture', 'emailEvery'] 
        
        def clean(self):
            cleaned_data = super(RegistrationForm, self).clean()
            if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError("Passwords don't match. Please enter both fields again.")
            return self.cleaned_data

        def save(self, commit=True):
            user = super(RegistrationForm, self).save(commit=False)
            user.set_password(self.cleaned_data['password1'])
            if commit:
                user.save()
            return user
        

class AuthenticationForm(forms.Form):
    """
    Login form
    """
    userName = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        fields = ['userName', 'password']
        
class EditProfileForm(forms.ModelForm):
    email = forms.CharField(max_length=75, widget=forms.EmailInput())
    CHOICES=[(0,'Immediate'),
         (10,'Every 10 minutes'), (60, 'Every hour')]
    emailEvery = forms.ChoiceField(label='Notification Frequency', choices=CHOICES)        
    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'picture', 'emailEvery'] 
        
class ChangePasswordForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Password (again)")

    class Meta:
        model = User
        fields = ('password1', 'password2')
                
    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Passwords don't match. Please enter both fields again.")
        return self.cleaned_data

    def save(self, commit=True):
        user = super(ChangePasswordForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user