import re

from django import forms
from pypdf.errors import PdfReadError
from pypdf import PdfReader
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class PDFFileUploadForm(forms.Form):
    file = forms.FileField(label='Файл', widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Здійснити', css_class='btn btn-primary'))
        self.helper.form_id = 'pdf_form'

    def clean_file(self):
        cleaned_data = self.clean()
        file = cleaned_data['file']
        try:
            reader = PdfReader(file)
            if reader.is_encrypted:
                raise forms.ValidationError('PDF файл зашифрований.')
        except PdfReadError:
            raise forms.ValidationError('Некорректний pdf файл.')
        else:
            return file


class PDFFileProtectForm(PDFFileUploadForm):
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(), label='Пароль', help_text='Пароль може містити латинські букви, цифри і !@#$%^&*()')

    def clean_password(self):
        cleaned_data = self.clean()
        password = cleaned_data['password']

        if len(password) < 3:
            raise forms.ValidationError('Пароль надто короткий.')

        elif not bool(re.match('^[0-9a-zA-Z!@#$%^&*()]{3,}$', password)):
            raise forms.ValidationError('Пароль містить некорректні символи.')

        return password






