import json
import httpretty
from aggregator.tests.factories import UserSocialAuthFactory
from aggregator.fetchers.github import GithubFetchStrategy
from aggregator.fetchers.facebook import FacebookFetchStrategy
from mock import patch
from rest_framework.test import APITestCase

import fakedata


class BaseFetchStrategyTestCase(APITestCase):

    def mock_avatar_request(self, url, target):
        httpretty.register_uri(
            httpretty.HTTPretty.GET,
            url,
            status=301,
            location=target
        )

        httpretty.register_uri(
            httpretty.HTTPretty.GET,
            target
        )

    def mock_collection_request(self, url, response_struct):
        httpretty.register_uri(
            httpretty.HTTPretty.GET,
            url,
            body=json.dumps(response_struct)
        )


class GithubFetchStrategyTest(BaseFetchStrategyTestCase):

    def setUp(self):
        self.fetcher = GithubFetchStrategy(UserSocialAuthFactory())
        self.api = 'https://api.github.com'

    @httpretty.activate
    def test_get_avatar_url_method(self):
        url = 'https://github.com/%s.png?size=200' % self.fetcher.login
        target = 'https://imgurl.com'

        self.mock_avatar_request(url, target)
        self.assertEqual(self.fetcher.get_avatar_url(), target)

    @httpretty.activate
    @patch(
        'aggregator.fetchers.github.GithubFetchStrategy.get_follower_name',
        lambda *args: 'Fname Lname'
    )
    def test_get_followers_method(self):
        self.mock_collection_request(
            '%s/user/followers' % self.api,
            fakedata.GITHUB_FOLLOWERS
        )

        self.assertEqual(self.fetcher.get_followers(), [{
            'name': 'Fname Lname',
            'uid': 1,
            'avatar_url': 'avaurl1'
        }, {
            'name': 'Fname Lname',
            'uid': 2,
            'avatar_url': 'avaurl2'
        }])

    @httpretty.activate
    def test_get_follower_name_method(self):
        requested_url = 'http://followerurl.com'

        httpretty.register_uri(
            httpretty.GET,
            requested_url,
            body='{"name": "Fname Lname"}'
        )

        name = self.fetcher.get_follower_name(requested_url)

        self.assertEqual(name, 'Fname Lname')

    @httpretty.activate
    def test_get_followers_count_method(self):
        self.mock_collection_request(
            '%s/user' % self.api,
            fakedata.GITHUB_USER_INFO
        )

        self.assertEqual(self.fetcher.get_followers_count(), 2)

    @httpretty.activate
    def test_get_user_info_method(self):
        url = self.api + '/user'
        self.mock_collection_request(url, fakedata.GITHUB_USER_INFO)

        data = self.fetcher.get_user_info()
        self.assertEqual(data, fakedata.USER_INFO)


class FacebookFetchStrategyTest(BaseFetchStrategyTestCase):

    def setUp(self):
        self.user_social_auth = UserSocialAuthFactory()
        self.fetcher = FacebookFetchStrategy(self.user_social_auth)
        self.api_url = 'https://graph.facebook.com/v2.7/me'

    @httpretty.activate
    def test_get_avatar_url_method(self):
        url = self.api_url + '/picture'
        target = 'https://imgurl.com'

        self.mock_avatar_request(url, target)
        self.assertEqual(self.fetcher.get_avatar_url(), target)

    @httpretty.activate
    def test_get_friends_method(self):
        url = self.api_url + '/friends'

        self.mock_collection_request(url, fakedata.FACEBOOK_FRIENDS['friends'])
        self.assertEqual(self.fetcher.get_friends(), [
            {'uid': 1, 'name': 'first friend', 'avatar_url': 'avaurl1'},
            {'uid': 2, 'name': 'second friend', 'avatar_url': 'avaurl2'}
        ])

    @httpretty.activate
    def test_get_friends_count_method(self):
        url = self.api_url

        self.mock_collection_request(url, fakedata.FACEBOOK_FRIENDS)
        self.assertEqual(self.fetcher.get_friends_count(), 2)

    @httpretty.activate
    def test_get_user_info_method(self):
        url = self.api_url
        self.mock_collection_request(url, fakedata.FACEBOOK_USER_INFO)

        data = self.fetcher.get_user_info()
        self.assertEqual(data, fakedata.USER_INFO)
