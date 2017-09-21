/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function () {
    'use strict';

    angular
        .module('testapiApp')
        .controller('ApplicationController', ApplicationController);

    ApplicationController.$inject = [
        '$http', '$stateParams', '$window',
        '$uibModal', 'testapiApiUrl', 'raiseAlert', 'ngDialog', '$scope'
    ];

    /**
     */
    function ApplicationController($http, $stateParams, $window,
        $uibModal, testapiApiUrl, raiseAlert, ngDialog, $scope) {

        var ctrl = this;

	function init(){
		ctrl.organization_name = null;
		ctrl.organization_web = null;
		ctrl.product_name = null;
		ctrl.product_documentation = null;
		ctrl.product_categories = "soft&hard";
		ctrl.user_id = null;
                ctrl.lab_location="internal";
                ctrl.lab_email=null;
		ctrl.applications = [];
		ctrl.showApplications = [];

		ctrl.totalItems = null;
		ctrl.currentPage = 1;
		ctrl.itemsPerPage = 5;
		ctrl.numPages = null;

		getApplication();
	}


	ctrl.submitForm = function(){
		var data = {
		    "organization_name": ctrl.organization_name,
		    "organization_web": ctrl.organization_web,
		    "product_name": ctrl.product_name,
		    "product_documentation": ctrl.product_documentation,
		    "product_categories": ctrl.product_categories,
		    "user_id": ctrl.user_id
		};
		console.log(data);
		$http.post(testapiApiUrl + "/cvp/applications", data).then(function(response){
			ngDialog.close();
			getApplication();
		}, function(error){
		});
	}

	ctrl.openConfirmModal = function(){
                ngDialog.open({
                    preCloseCallback: function(value) {
                    },
                    template: 'testapi-ui/components/application/modal/confirmModal.html',
                    scope: $scope,
                    className: 'ngdialog-theme-default custom-width-60',
                    showClose: true,
                    closeByDocument: true
                });
	}

	ctrl.cancelSubmit = function(){
		ngDialog.close();
	}

	ctrl.updatePage = function(){
            getApplication();
	}

	function getApplication(){
		$http.get(testapiApiUrl + "/cvp/applications?page="+ctrl.currentPage+"&signed&per_page="+ctrl.itemsPerPage).then(function(response){
			ctrl.applications = response.data.applications;
                        ctrl.totalItems = response.data.pagination.total_pages* ctrl.itemsPerPage;
                        ctrl.currentPage = response.data.pagination.current_page;
                        ctrl.numPages = response.data.pagination.total_pages;
		}, function(error){
		});
	}

	init();
    }
})();
