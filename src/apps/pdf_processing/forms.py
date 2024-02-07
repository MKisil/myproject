import re

from django import forms
from pypdf.errors import PdfReadError, FileNotDecryptedError
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
        file = self.cleaned_data['file']
        try:
            reader = PdfReader(file)
        except PdfReadError:
            raise forms.ValidationError('Incorrect pdf file.')
        else:
            return file


class PDFFileEncryptForm(PDFFileUploadForm):
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(), label='Пароль',
                               help_text='Пароль може містити латинські букви, цифри і !@#$%^&*()')

    def clean_password(self):
        password = self.cleaned_data['password']

        if len(password) < 3:
            raise forms.ValidationError('Пароль надто короткий.')

        elif not bool(re.match('^[0-9a-zA-Z!@#$%^&*()]{3,}$', password)):
            raise forms.ValidationError('Пароль містить некорректні символи.')

        return password


class PDFFileDecryptForm(PDFFileUploadForm):
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(), label='Пароль',
                               help_text='Введіть пароль, яким зашифровано pdf файл')

    def clean(self):
        super(PDFFileDecryptForm, self).clean()
        file = self.cleaned_data['file']
        password = self.cleaned_data['password']
        try:
            reader = PdfReader(file)
            if not reader.is_encrypted:
                raise forms.ValidationError('PDF файл не зашифрований.')
            if not reader.decrypt(password):
                raise forms.ValidationError('Невірний пароль.')
        except PdfReadError:
            raise forms.ValidationError('Некорректний pdf файл.')

        return self.cleaned_data

    def clean_file(self):
        return self.cleaned_data['file']


class PDFFileSplitForm(PDFFileUploadForm):
    password = forms.CharField(max_length=200, required=False)
    selected_pages = forms.CharField(max_length=1000)
    save_separate = forms.BooleanField()

    def clean_password(self):
        return self.cleaned_data['password']

    def clean_selected_pages(self):
        selected_pages = self.cleaned_data['selected_pages']

        if not selected_pages.replace(',', '').isdigit():
            raise forms.ValidationError('Incorrect page numbers.')

        return selected_pages

    def clean_save_separate(self):
        save_separate = self.cleaned_data['save_separate']

        if save_separate == 'on':
            return True
        else:
            return False


class PDFFileAddPageNumbersForm(PDFFileUploadForm):
    password = forms.CharField(max_length=200, required=False)
    number_position = forms.CharField(max_length=10)
    number_on_first_page = forms.BooleanField(required=False)

    def clean_number_position(self):
        number_position = self.cleaned_data['number_position']

        if number_position not in ['l-top', 'c-top', 'r-top', 'l-bottom', 'c-bottom', 'r-bottom']:
            raise forms.ValidationError('Incorrect position value for page numbers.')
        return number_position


class PDFFileRotateForm(PDFFileUploadForm):
    password = forms.CharField(max_length=200, required=False)
    document_rotation = forms.DecimalField(min_value=-270, max_value=270)
    pages_rotation = forms.JSONField()

    def clean_document_rotation(self):
        return int(self.cleaned_data['document_rotation'])

    def clean_pages_rotation(self):
        pages_rotation = self.cleaned_data['pages_rotation']

        if not ''.join(pages_rotation.keys()).replace('-', '0').isdigit():
            raise forms.ValidationError('Incorrect page numbers.')

        if len([angl for angl in pages_rotation.values() if angl % 10 == 0]) != len(pages_rotation.values()):
            raise forms.ValidationError('Incorrect rotating angles for pages.')

        return pages_rotation
