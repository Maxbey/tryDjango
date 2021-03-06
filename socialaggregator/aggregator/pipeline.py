from django.core.cache import cache
from celery import chord
from social.apps.django_app.default.models import UserSocialAuth

import tasks
from .fetchers.factory import SocialFetchStrategyFactory


def get_strategy(account):
    return SocialFetchStrategyFactory.fabricate(
        account.provider,
        account
    )


def load_social_data(social, *args, **kwargs):
    task_pipeline = [
        tasks.fetch_avatar_url.s(social.id),
        tasks.fetch_user_info.s(social.id)
    ]

    account = UserSocialAuth.objects.get(pk=social.id)
    strategy = get_strategy(account)

    if 'friends' in strategy.relations:
        task_pipeline.append(tasks.fetch_user_friends_count.s(social.id))

        friends_async = tasks.fetch_user_friends.apply_async(
            (social.id,),
            link=tasks.create_social_persons.s(
                account_pk=social.id, person_type='friend')
        )

        cache.set('fetch_user_friends', friends_async.task_id)

    if 'followers' in strategy.relations:
        task_pipeline.append(tasks.fetch_user_followers_count.s(social.id))

        followers_async = tasks.fetch_user_followers.apply_async(
            (social.id,),
            link=tasks.create_social_persons.s(
                account_pk=social.id, person_type='follower')
        )

        cache.set('fetch_user_followers', followers_async.task_id)

    pipeline_async = chord(task_pipeline)(tasks.save_social_data.s(pk=social.id))

    cache.set('save_social_data', pipeline_async.task_id)
