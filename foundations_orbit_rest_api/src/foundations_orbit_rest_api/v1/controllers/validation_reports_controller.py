
from foundations_core_rest_api_components.utils.api_resource import api_resource


@api_resource('/api/v1/projects/<string:project_name>/validation_results')
class ValidationReportsController(object):
    
    def post(self):
        from foundations_core_rest_api_components.lazy_result import LazyResult
        from foundations_core_rest_api_components.response import Response
        from foundations_orbit_rest_api.v1.models.validation_report_listing import ValidationReportListing
        from foundations_orbit_rest_api.v1.models.validation_report import ValidationReport

        inference_period = self.params.pop('inference_period')
        monitor_package = self.params.pop('monitor_package')
        data_contract = self.params.pop('data_contract')
        project_name = self.params.pop('project_name')

        listing_object = ValidationReportListing(inference_period=inference_period, monitor_package=monitor_package, data_contract=data_contract)
        response = ValidationReport.get(project_name=project_name, listing_object=listing_object)
        
        failure_response_data = {
            'inference_period': inference_period,
            'monitor_package': monitor_package,
            'data_contract': data_contract,
            'error': 'does not exist'
        }

        fallback = Response('asdf', LazyResult(lambda: failure_response_data), status=404)

        return Response('asdf', response, status=200, fallback=fallback)

