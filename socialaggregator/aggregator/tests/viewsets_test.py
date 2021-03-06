import json
from mock import patch, PropertyMock
from rest_framework import status
from rest_framework.test import APITestCase

from aggregator.models import SocialPerson

from aggregator.views import DependsOnCeleryMixin
from .factories import UserSocialAuthFactory, SocialPersonFactory
from .factories import UserFactory

from .helpers import get_authorized_client, fill_instance, dict_from_model, is_models_equal

from fetchers.fakedata import SOCIAL_DATA_RESPONSE


class Strategy(object):

    @property
    def relations(self):
        return SOCIAL_DATA_RESPONSE['social_relations']

    def get_avatar_url(self):
        return SOCIAL_DATA_RESPONSE['avatar_url']

    def get_followers_count(self):
        return 2

    def get_friends_count(self):
        return 2

    def get_user_info(self):
        return SOCIAL_DATA_RESPONSE['user_info']


def get_strategy(a, b):
    return Strategy()


class BaseViewSetTestCase(APITestCase):
    model_attributes = []
    required_attributes = []

    def set_model_attributes(self, attributes):
        self.model_attributes = attributes

    def set_required_attributes(self, attributes):
        self.required_attributes = attributes

    def get_authorized_client(self, user):
        return get_authorized_client(user)

    def get_authorized_client_with_account(self):
        account = UserSocialAuthFactory()
        return self.get_authorized_client(account.user), account

    def assert_unauthorized(self, response):
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data, {'detail': 'Authentication credentials were not provided.'})

    def assert_bad_request(self, response, error_message, exclude=None):
        if exclude is None:
            exclude = []

        expected_errors = {
            attribute: [error_message] for attribute in self.required_attributes if attribute not in exclude
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_errors)

    def assert_expected_model_response(self, response, instance, model_relations):
        expected_instance = dict_from_model(
            instance, self.model_attributes, model_relations)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_instance)

    def assert_changes_in_db(self, expected_instance):
        model = type(expected_instance)
        instance = model.objects.get(pk=expected_instance.id)
        self.assertTrue(is_models_equal(expected_instance,
                                        instance, self.model_attributes))


class UserSocialAuthViewSet(BaseViewSetTestCase):

    def setUp(self):
        self.set_model_attributes(['id', 'provider', 'uid', 'user'])

        self.first_fixture = self.get_authorized_client_with_account()
        self.second_fixture = self.get_authorized_client_with_account()

        self.url = '/api/social_account/'

    def test_unauthorized_attempt_to_retrieve_account(self):
        response = self.client.get(self.url)
        self.assert_unauthorized(response)

    @patch('aggregator.serializers.UserSocialAuthSerializer.get_strategy', get_strategy)
    @patch('aggregator.views.DependsOnCeleryMixin.is_task_done')
    def test_accounts_list_when_celery_not_processing(self, is_task_done):
        is_task_done.return_value = True

        response = self.first_fixture[0].get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_response = dict_from_model(
            self.first_fixture[1],
            self.model_attributes, ['user']
        )

        expected_response['social_data'] = SOCIAL_DATA_RESPONSE

        self.assertEqual(
            response.json()[0],
            expected_response
        )

    @patch('aggregator.views.DependsOnCeleryMixin.is_task_done')
    def test_accounts_list_when_celery_processing(self, is_task_done):
        is_task_done.return_value = False

        response = self.first_fixture[0].get(self.url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual('CELERY_PROCESSING', json.loads(response.content))

    @patch('aggregator.serializers.UserSocialAuthSerializer.get_strategy', get_strategy)
    def test_list_only_owner_accounts(self):
        first_user_account = self.first_fixture[0].get(self.url).json()[0]
        second_user_account = self.second_fixture[0].get(self.url).json()[0]

        self.assertNotEqual(first_user_account, second_user_account)

    def test_destroy_account(self):
        deletion_url = '/api/social_account/%d/' % self.first_fixture[1].id
        response = self.first_fixture[0].delete(deletion_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_destroy_not_by_owner(self):
        deletion_url = '/api/social_account/%d/' % self.second_fixture[1].id
        response = self.first_fixture[0].delete(deletion_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserViewSetTest(BaseViewSetTestCase):

    def setUp(self):
        self.set_model_attributes(
            ['id', 'username', 'last_name', 'first_name', 'email'])
        self.set_required_attributes(['username'])

        self.user = UserFactory()
        self.authorized_client = self.get_authorized_client(self.user)
        self.url = '/api/user/'

    def test_unauthorized_attempt_to_retrieve_user(self):
        response = self.client.get(self.url)
        self.assert_unauthorized(response)

    def test_authorized_attempt_to_retrieve_user_(self):
        response = self.authorized_client.get(self.url)
        self.assert_expected_model_response(response, self.user, [])

    def test_unauthorized_attempt_to_update_user(self):
        response = self.client.put(self.url, data={})
        self.assert_unauthorized(response)

    def test_authorized_attempt_to_update_user(self):
        request_payload = {
            'username': 'newusername',
            'last_name': 'newlastname',
            'first_name': 'newfirstname',
            'email': 'newemail@email.com'
        }

        response = self.authorized_client.put(self.url, request_payload)

        fill_instance(self.user, request_payload)
        self.assert_expected_model_response(response, self.user, [])
        self.assert_changes_in_db(self.user)

    def test_invalid_request_payload_to_update(self):
        response = self.authorized_client.put(self.url, {})
        self.assert_bad_request(
            response, error_message='This field is required.')


class SocialPersonViewSetTest(BaseViewSetTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.authorized_client = self.get_authorized_client(self.user)
        self.url = '/api/social_person/'
        self.set_model_attributes(
            ['id', 'uid', 'name', 'avatar_url', 'email',
                'provider', 'social_person_type']
        )

    def test_unauthorized_attempt_to_list_persons(self):
        response = self.client.get(self.url)
        self.assert_unauthorized(response)

    @patch('aggregator.views.DependsOnCeleryMixin.is_task_done')
    def test_list_when_celery_not_processing(self, is_task_done):
        is_task_done.return_value = True

        for i in xrange(0, 3):
            persons = []

            for j in xrange(0, 2):
                persons.append(SocialPersonFactory())

            account = UserSocialAuthFactory()
            account.user = self.user
            account.save()

            account.socialperson_set.set(persons)

        response = self.authorized_client.get(self.url)

        expected_response = {'count': 6,
                             'previous': None, 'next': None, 'results': []}

        for person in SocialPerson.objects.all():
            expected_response['results'].append(
                dict_from_model(person, self.model_attributes, [])
            )

        self.assertEqual(expected_response, json.loads(response.content))

    @patch('aggregator.views.DependsOnCeleryMixin.is_task_done')
    def test_list_when_celery_processing(self, is_task_done):
        is_task_done.return_value = False

        response = self.authorized_client.get(self.url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual('CELERY_PROCESSING', json.loads(response.content))


class DependsOnCeleryMixinTest(APITestCase):

    @patch('aggregator.views.cache.get')
    def test_task_id_not_exist_in_cache(self, get):
        get.return_value = None

        mixin = DependsOnCeleryMixin()

        self.assertTrue(mixin.is_task_done('name'))

    @patch('aggregator.views.AsyncResult.status', new_callable=PropertyMock)
    @patch('aggregator.views.cache.get')
    def test_task_should_not_be_finished(self, get, status):
        get.return_value = 'taskid'
        status.return_value = 'PENDING'

        mixin = DependsOnCeleryMixin()

        self.assertFalse(mixin.is_task_done('name'))

    @patch('aggregator.views.AsyncResult.status', new_callable=PropertyMock)
    @patch('aggregator.views.cache.get')
    def test_task_should_be_finished(self, get, status):
        get.return_value = 'taskid'
        status.return_value = 'SUCCESS'

        mixin = DependsOnCeleryMixin()

        self.assertTrue(mixin.is_task_done('name'))
