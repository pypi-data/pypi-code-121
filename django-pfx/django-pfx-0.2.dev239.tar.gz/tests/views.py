import logging

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Count, Q
from django.utils.translation import gettext as _

from pfx.pfxcore.decorator import rest_api, rest_view
from pfx.pfxcore.http import JsonResponse
from pfx.pfxcore.views import (
    VF,
    BaseRestView,
    Filter,
    FilterGroup,
    MediaRestViewMixin,
    ModelFilter,
    RestView,
    SlugDetailRestViewMixin,
)

from .models import Author, Book, BookType

logger = logging.getLogger(__name__)


class AuthorRestViewMixin():
    model = Author
    fields = [
        'first_name', 'last_name', 'name_length', 'slug', 'gender',
        VF('books', readonly=True), VF('created_at', readonly=True),
        VF('create_comment', readonly_update=True),
        VF('update_comment', readonly_create=True)]
    list_fields = ['first_name', 'last_name', 'gender']


def heroic_fantasy_filter(value):
    q = Q(last_name="Tolkien")
    return value and q or ~q


def last_name_filter(value):
    return Q(last_name__isnull=not value)


def last_name_choices_filter(value):
    return Q(last_name=value)


def pub_date_gte_filter(value):
    return Q(pub_date__gte=value)


def author_pk_filter(value):
    return Q(author__pk=value)


@rest_view("/authors")
class AuthorRestView(AuthorRestViewMixin, SlugDetailRestViewMixin, RestView):
    default_public = True
    filters = [
        FilterGroup('book_gender', _("Book Gender"), [
            ModelFilter(Author, 'science_fiction'),
            Filter(
                'heroic_fantasy', _("Heroic Fantasy"),
                Filter.BooleanField, heroic_fantasy_filter),
        ]),
        FilterGroup('custom', _("Custom"), [
            ModelFilter(
                Author, 'last_name', type=Filter.BooleanField,
                filter_func=last_name_filter),
            ModelFilter(Author, 'first_name'),
            ModelFilter(Author, 'gender'),
            Filter(
                'last_name_choices', _("Tolien or Asimov"),
                Filter.CharField, last_name_choices_filter,
                choices=[('Tolkien', "Tolkien"), ('Asimov', "Asimov")]),
        ]),
    ]

    def search_filter(self, search):
        return (
            Q(first_name__unaccent__icontains=search) |
            Q(last_name__unaccent__icontains=search))

    @rest_api("/cache/<int:id>", method="get")
    def cache_get(self, id, *args, **kwargs):
        book = Author.cache_get(id)
        if book:
            return self.response(book, from_cache=True)
        book = self.get_object(pk=id)
        book.cache()
        return self.response(book, from_cache=False)


@rest_view("/authors-annotate")
class AuthorAnnotateRestView(AuthorRestView):
    fields = [
        'first_name', 'last_name', 'slug',
        'books_count', 'books_count_annotate', 'books_count_prop']
    list_fields = [
        'first_name', 'last_name', 'slug',
        'books_count', 'books_count_annotate', 'books_count_prop']

    def get_queryset(self):
        return super().get_queryset().annotate(
            books_count_annotate=Count('books'))


@rest_view("/authors-fields-props")
class AuthorFieldsPropsRestView(AuthorRestView):
    fields = [
        'first_name', 'last_name', 'slug',
        VF('books_count', "Books Count", "IntegerField"),
        VF('books_count_annotate', "Books Count (annotate)", "IntegerField"),
        VF('books_count_prop', "Books Count (property)", "IntegerField")]
    list_fields = [
        'first_name', 'last_name', 'slug',
        VF('books_count', "B.C.", "IntegerField"),
        VF('books_count_annotate', "B.C. (a)", "IntegerField"),
        VF('books_count_prop', "B.C. (p)", "IntegerField")]

    def get_queryset(self):
        return super().get_queryset().annotate(
            books_count_annotate=Count('books'))


@rest_view("/private-edit/authors")
class PrivateEditAuthorRestView(AuthorRestViewMixin, RestView):
    get_public = True
    get_list_public = True


@rest_view("/private/authors")
class PrivateAuthorRestView(AuthorRestViewMixin, RestView):
    pass


@rest_view("/admin-edit/authors")
class AdminEditAuthorRestView(AuthorRestViewMixin, RestView):
    def put_perm(self, id, *args, **kwargs):
        return self.request.user.is_superuser


@rest_view("/admin/authors")
class AdminAuthorRestView(AuthorRestViewMixin, RestView):
    def perm(self):
        return self.request.user.is_superuser


@rest_view("/books")
class BookRestView(MediaRestViewMixin, RestView):
    model = Book
    fields = [
        'name', 'author', 'pub_date', VF('created_at', readonly=True),
        'type', 'cover', 'pages', 'rating', 'author__last_name',
        'read_time']
    default_public = True
    filters = [
        FilterGroup('custom', _("Custom"), [
            ModelFilter(Book, 'author'),
            ModelFilter(Book, 'type'),
            ModelFilter(Book, 'pages'),
            ModelFilter(Book, 'rating'),
            ModelFilter(Book, 'pub_date'),
            Filter(
                'pub_date_gte', _("Publication Date greater than"),
                Filter.DateField, pub_date_gte_filter),
            Filter(
                'author_pk', _("Author PK"),
                Filter.ForeignKey, author_pk_filter,
                related_model="Author"),
        ]),
    ]


def author_json_repr(obj):
    return obj.json_repr(
        hello="World",
        last_name=obj.last_name)


@rest_view("/books-custom-author")
class BookCustomAuthorRestView(BookRestView):
    fields = [
        VF('name', alias='book_name'),
        VF('author', json_repr=author_json_repr),
        VF('author__last_name', alias='author_last_name'),
        'pub_date']


@rest_view("/book-types")
class BookTypeRestView(RestView):
    model = BookType
    fields = ['name', 'slug']
    default_public = True


@rest_view("/test-i18n")
class Testi18nView(BaseRestView):
    default_public = True

    @rest_api("", method="get")
    def get(self, *args, **kwargs):
        return JsonResponse({'Monday': _("Monday")})


@rest_view("/error")
class TestErrorView(BaseRestView):
    default_public = True

    @rest_api("/500", method="get")
    def raise_500(self):
        raise ImproperlyConfigured("Test exception")
