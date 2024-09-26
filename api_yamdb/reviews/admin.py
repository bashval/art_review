from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'author',
    )
    search_fields = ('author',)
    list_filter = ('author',)


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)


class GenreInline(admin.TabularInline):
    model = GenreTitle
    extra = 1


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'year',
    )
    search_fields = ('name',)
    list_filter = ('category',)
    inlines = (GenreInline,)


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'author',
        'score',
    )
    search_fields = ('author',)
    list_filter = ('author', 'score')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Title, TitleAdmin)
