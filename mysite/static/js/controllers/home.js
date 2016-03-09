var myAppModule = angular.module('baseApp', [])

.controller('UserController',
  function($scope, $http) {
    $scope.loggedIn = false;
    $http.get('/api/currentuser').success(function(data, status, headers, config) {
      if(data.username){
        $scope.username = data.username;
        $scope.loggenIn = true;
      }
    });
});
