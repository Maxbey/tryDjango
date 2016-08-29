'use strict';

/**
 * @ngdoc function
 * @name spaApp.controller:RegisterController
 * @description
 * # RegisterController
 * Controller of the spaApp
 */
angular.module('spaApp')
  .controller('RegisterController', function(AuthenticationService, ToastService, $state, ResponseService, FormService) {
    var vm = this;

    vm.register = register;
    vm.resetServerValidation = resetServerValidation;

    function resetServerValidation(formField) {
      FormService.resetServerValidation(formField, 'serverValidation');
    }

    function register(form) {
      AuthenticationService.register(
        vm.email,
        vm.password1,
        vm.password2,
        vm.username
      ).then(function(response) {
        $state.go('enter.login');
        ToastService.show('You are successfully registered');
      }, function(response) {
        vm.backendValidationErrors = ResponseService.parseResponseErrors(response.data);
        FormService.setServerValidation(form, vm.backendValidationErrors, 'serverValidation');
      });
    }
  });
