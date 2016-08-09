from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from social.apps.django_app.default.models import UserSocialAuth

from .fetchers.factory import SocialFetchStrategyFactory


class UserSocialAuthSerializer(ModelSerializer):
    social_data = serializers.SerializerMethodField()

    def get_social_data(self, account):
        strategy = SocialFetchStrategyFactory.fabricate(
            account.provider,
            account
        )

        social_data = account.extra_data['social_data']

        followers_count = len(social_data['followers']) \
            if 'followers' in social_data else 0

        friends_count = len(social_data['friends']) \
            if 'friends' in social_data else 0

        data = {
            'avatar_url': social_data['avatar_url'],
            'counts': {
                'followers': followers_count,
                'friends': friends_count
            },
            'user_info': social_data['user_info'],
            'social_relations': strategy.relations
        }

        return data

    class Meta:
        model = UserSocialAuth
        exclude = ('extra_data',)
