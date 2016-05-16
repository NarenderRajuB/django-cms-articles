from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.utils.i18n import get_language_tuple
from cms.models import Page

from django import forms
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms.utils import ErrorList
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _, get_language

from ..conf import settings
from ..models import Article, Title, EmptyTitle
from ..utils import is_valid_article_slug


class ArticleForm(forms.ModelForm):
    language            = forms.ChoiceField(label=_('Language'), choices=get_language_tuple(),
                            help_text=_('The current language of the content fields.'))
    title               = Title._meta.get_field('title').formfield()
    slug                = Title._meta.get_field('slug').formfield()
    description         = Title._meta.get_field('description').formfield()
    page_title          = Title._meta.get_field('page_title').formfield()
    menu_title          = Title._meta.get_field('menu_title').formfield()
    meta_description    = Title._meta.get_field('meta_description').formfield()
    image               = Title._meta.get_field('image').formfield()

    class Meta:
        model = Article
        fields = ['tree', 'template', 'login_required']

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['language'].widget = forms.HiddenInput()
        if self.fields['tree'].widget.choices.queryset.count() == 1:
            self.fields['tree'].initial = self.fields['tree'].widget.choices.queryset.first()
            self.fields['tree'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = self.cleaned_data
        slug = cleaned_data.get('slug', '')

        article = self.instance
        lang = cleaned_data.get('language', None)
        # No language, can not go further, but validation failed already
        if not lang:
            return cleaned_data
        tree = self.cleaned_data.get('tree', None)
        if tree and not is_valid_article_slug(article, lang, slug):
            self._errors['slug'] = ErrorList([_('Another article with this slug already exists')])
            del cleaned_data['slug']
        return cleaned_data

    def clean_slug(self):
        slug = slugify(self.cleaned_data['slug'])
        if not slug:
            raise ValidationError(_('Slug must not be empty.'))
        return settings.CMS_ARTICLES_SLUG_FORMAT.format(
            now = self.instance.creation_date or now(),
            slug = slug,
        )


class PublicationDatesForm(forms.ModelForm):
    language = forms.ChoiceField(label=_("Language"), choices=get_language_tuple(),
                                 help_text=_('The current language of the content fields.'))

    def __init__(self, *args, **kwargs):
        super(PublicationDatesForm, self).__init__(*args, **kwargs)
        self.fields['language'].widget = forms.HiddenInput()

    class Meta:
        model = Article
        fields = ['publication_date', 'publication_end_date']


