from rest_framework import serializers

from bookmarks.models import Bookmark, Tag, build_tag_string
from bookmarks.services.bookmarks import create_bookmark, update_bookmark
from bookmarks.services.tags import get_or_create_tag


class TagListField(serializers.ListField):
    child = serializers.CharField()


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = [
            'id',
            'url',
            'title',
            'description',
            'website_title',
            'website_description',
            'is_archived',
            'unread',
            'tag_names',
            'date_added',
            'date_modified'
        ]
        read_only_fields = [
            'website_title',
            'website_description',
            'date_added',
            'date_modified'
        ]

    # Override optional char fields to provide default value
    title = serializers.CharField(required=False, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')
    is_archived = serializers.BooleanField(required=False, default=False)
    unread = serializers.BooleanField(required=False, default=False)
    # Override readonly tag_names property to allow passing a list of tag names to create/update
    tag_names = TagListField(required=False, default=[])

    def create(self, validated_data):
        bookmark = Bookmark()
        bookmark.url = validated_data['url']
        bookmark.title = validated_data['title']
        bookmark.description = validated_data['description']
        bookmark.is_archived = validated_data['is_archived']
        bookmark.unread = validated_data['unread']
        tag_string = build_tag_string(validated_data['tag_names'])
        return create_bookmark(bookmark, tag_string, self.context['user'])

    def update(self, instance: Bookmark, validated_data):
        # Update fields if they were provided in the payload
        for key in ['url', 'title', 'description', 'unread']:
            if key in validated_data:
                setattr(instance, key, validated_data[key])

        # Use tag string from payload, or use bookmark's current tags as fallback
        tag_string = build_tag_string(instance.tag_names)
        if 'tag_names' in validated_data:
            tag_string = build_tag_string(validated_data['tag_names'])

        return update_bookmark(instance, tag_string, self.context['user'])


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'date_added']
        read_only_fields = ['date_added']

    def create(self, validated_data):
        return get_or_create_tag(validated_data['name'], self.context['user'])
