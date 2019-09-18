"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

class ReportFormatter(object):

    def __init__(self, inference_period, model_package, contract_name, validation_report, options):
        self._inference_period = inference_period
        self._model_package = model_package
        self._contract_name = contract_name
        self._validation_report = validation_report
        self._options = options

    def formatted_report(self):
        return {
            'date': self._inference_period,
            'model_package': self._model_package,
            'data_contract': self._contract_name,
            'row_cnt_diff': self._formatted_row_count_difference_report(),
            'schema': self._formatted_schema_report(),
            'data_quality': self._formatted_data_quality_report() or {},
            'population_shift': self._formatted_population_shift_report() or {}
        }

    def serialized_output(self):
        import pickle
        return pickle.dumps(self.formatted_report())

    def _formatted_row_count_difference_report(self):
        return self._validation_report.get('row_cnt_diff', 0)

    def _formatted_schema_report(self):
        columns_in_reference, columns_in_current = self._columns_in_dataframes()

        columns_in_reference = set(columns_in_reference)
        number_of_columns_in_reference = len(columns_in_reference)

        columns_in_current = set(columns_in_current)
        number_of_columns_in_current = len(columns_in_current)

        columns_in_common = columns_in_reference.intersection(columns_in_current)
        number_of_healthy_columns = len(columns_in_common)

        width_of_widest_dataframe = max(number_of_columns_in_current, number_of_columns_in_reference)
        number_of_critical_columns = width_of_widest_dataframe - number_of_healthy_columns

        schema_report = {
            'summary': {
                'healthy': number_of_healthy_columns,
                'critical': number_of_critical_columns,
                'warning': 0
            }
        }
        if self._validation_report['schema_check_results']['passed']:
            schema_report['details_by_attribute'] = self._attribute_details_for_all_columns_as_healthy()
            return schema_report

        error_message = self._validation_report['schema_check_results']['error_message']

        if error_message == 'column sets not equal':
            missing_current_attribute_details = self._attribute_details_for_missing_columns('current')
            missing_reference_attribute_details = self._attribute_details_for_missing_columns('reference')
            details_by_attribute = missing_current_attribute_details + missing_reference_attribute_details
            if details_by_attribute:
                schema_report['details_by_attribute'] = details_by_attribute

        elif error_message == 'columns not in order':
            columns_out_of_order = self._validation_report['schema_check_results']['columns_out_of_order']
            number_of_columns_out_of_order = len(columns_out_of_order)
            number_of_columns = len(self._validation_report['metadata']['reference_metadata']['column_names'])

            schema_report = {
                'summary': {
                    'healthy': number_of_columns - number_of_columns_out_of_order,
                    'critical': number_of_columns_out_of_order,
                    'warning': 0
                }
            }

            details_by_attribute = self._attribute_details_for_out_of_order_columns()
            if details_by_attribute:
                schema_report['details_by_attribute'] = details_by_attribute

        elif error_message == 'column datatype mismatches':
            columns_mismatched = self._validation_report['schema_check_results']['cols']
            number_of_columns_mismatched = len(columns_mismatched)
            number_of_columns = len(self._validation_report['metadata']['reference_metadata']['column_names'])

            schema_report = {
                'summary': {
                    'healthy': number_of_columns - number_of_columns_mismatched,
                    'critical': number_of_columns_mismatched,
                    'warning': 0
                }
            }

            details_by_attribute = self._attribute_details_for_mismatched_columns()
            if details_by_attribute:
                schema_report['details_by_attribute'] = details_by_attribute

        return schema_report

    def _attribute_details_for_all_columns_as_healthy(self):
        type_mapping = self._validation_report['metadata']['current_metadata']['type_mapping']
        columns_in_current = self._columns_for_dataframe('current')
        details_for_attribute = []
        for column in columns_in_current:
            details_for_attribute.append({
                'attribute_name': column,
                'data_type': type_mapping[column],
                'issue_type': None,
                'validation_outcome': 'healthy'
            })
        return details_for_attribute

    def _attribute_details_for_missing_columns(self, column_type):
        missing_column_check = 'missing_in_ref' if column_type == 'reference' else 'missing_in_current'
        metadata = 'current_metadata' if column_type == 'reference' else 'reference_metadata'

        details_by_attribute = []
        missing_columns = self._validation_report['schema_check_results'][missing_column_check]
        type_mapping = self._validation_report['metadata'][metadata]['type_mapping']

        for missing_column in missing_columns:
            missing_data_type = type_mapping[missing_column]

            details_by_attribute.append({
                'attribute_name': missing_column,
                'data_type': missing_data_type,
                'issue_type': f'missing in {column_type} dataframe',
                'validation_outcome': 'critical'
            })

        return details_by_attribute

    def _attribute_details_for_out_of_order_columns(self):
        details_by_attribute = []

        type_mapping = self._validation_report['metadata']['reference_metadata']['type_mapping']
        columns_out_of_order = self._validation_report['schema_check_results']['columns_out_of_order']
        for column_out_of_order in columns_out_of_order:
            col_data_type = type_mapping[column_out_of_order]

            details_by_attribute.append({
                'attribute_name': column_out_of_order,
                'data_type': col_data_type,
                'issue_type': 'column is out of order',
                'validation_outcome': 'critical'
            })

        return details_by_attribute

    def _attribute_details_for_mismatched_columns(self):
        reference_type_mapping = self._validation_report['metadata']['reference_metadata']['type_mapping']
        current_type_mapping = self._validation_report['metadata']['current_metadata']['type_mapping']
        details_by_attribute = []

        columns_mismatched = self._validation_report['schema_check_results']['cols']
        for column_mismatched in columns_mismatched:
            details_by_attribute.append({
                'attribute_name': column_mismatched,
                'data_type': current_type_mapping[column_mismatched],
                'issue_type': f'datatype in reference dataframe is {reference_type_mapping[column_mismatched]}',
                'validation_outcome': 'critical'
            })
        return details_by_attribute

    def _formatted_data_quality_report(self):
        if not self._options.check_distribution:
            return None
        dist_check_results = self._validation_report['dist_check_results']

        data_quality_summary = {
            'healthy': 0,
            'critical': 0,
            'warning': 0
        }
        data_quality_attribute_details = []
        
        for col, col_results in dist_check_results.items():
            for sv, sv_dict in col_results['special_values'].items():
                attribute_details = dict()
                attribute_details["attribute_name"] = col
                attribute_details["value"] = str(sv)
                attribute_details["pct_in_reference_data"] = sv_dict['ref_percentage']
                attribute_details["pct_in_current_data"] = sv_dict['current_percentage']
                attribute_details["difference_in_pct"] = sv_dict['percentage_diff']
                attribute_details["validation_outcome"] = "healthy" if sv_dict["passed"] else "critical"
                data_quality_attribute_details.append(attribute_details)
                if sv_dict["passed"]:
                    data_quality_summary['healthy'] += 1
                else:
                    data_quality_summary['critical'] += 1

        return {
            'summary': data_quality_summary,
            'details_by_attribute': data_quality_attribute_details
        }
    
    def _formatted_population_shift_report(self):
        if not self._options.check_distribution:
            return None

        dist_check_results = self._validation_report['dist_check_results']
        
        population_shift_summary = {
            'healthy': 0,
            'critical': 0,
            'warning': 0
        }
        population_shift_attribute_details = []

        for column, col_results in dist_check_results.items():
            population_shift_attribute_details.append({
                'attribute_name': column,
                'L-infinity': col_results['binned_l_infinity'],
                'validation_outcome': 'healthy' if col_results['binned_passed'] else 'critical',
            })
            
            if col_results['binned_passed']:
                population_shift_summary['healthy'] += 1
            else:
                population_shift_summary['critical'] += 1

        return {
            'summary': population_shift_summary,
            'details_by_attribute': population_shift_attribute_details
        }

    def _columns_in_dataframes(self):
        columns_in_reference = self._columns_for_dataframe('reference')
        columns_in_current = self._columns_for_dataframe('current')

        return columns_in_reference, columns_in_current

    def _columns_for_dataframe(self, dataframe_name):
        report_metadata = self._validation_report['metadata']

        metadata = report_metadata[f'{dataframe_name}_metadata']
        return metadata['column_names']