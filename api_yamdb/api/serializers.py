from rest_framework import serializers


from reviews.models import Comment, Review


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title_id')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title_id'),
                message='Можно написать только один отзыв к тайтлу'
            ),
        )
        read_only_fields = ('title_id',)

    def validate_score(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError(
                'Оценка тайтлу должна быть целым числом'
            )

        if not (1 <= value <= 10):
            raise serializers.ValidationError('Оценка должна быть от 1 до 10')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('title_id', None)
        return representation


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'pub_date', 'author', 'review_id')
        read_only_fields = ('review_id',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('review_id', None)
        return representation
