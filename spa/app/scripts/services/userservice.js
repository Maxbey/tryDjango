'use strict';

/**
 * @ngdoc service
 * @name spaApp.UserService
 * @description
 * # UserService
 * Service in the spaApp.
 */
angular.module('spaApp')
  .service('UserService', function ($http, envConfig) {
    var baseUrl = envConfig.BACKEND_HOST + '/api';

    return {
      update: update,
      accounts: accounts,
      removeAccount: removeAccount
    };

    function update(user) {
      return $http.put(baseUrl + '/user/', user);
    }

    function accounts() {
      return $http.get(baseUrl + '/social_account/');
    }

    function removeAccount(accountId) {
      return $http.delete(baseUrl + '/social_account/' + accountId + '/')
    }
  });
