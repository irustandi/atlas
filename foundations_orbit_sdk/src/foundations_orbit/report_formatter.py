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
        row_cnt_diff = self._validation_report.get('row_cnt_diff', 0)

        report_metadata = self._validation_report['metadata']

        reference_metadata = report_metadata['reference_metadata']
        reference_column_names = reference_metadata['column_names']
        number_of_columns_in_reference = len(reference_column_names)

        current_metadata = report_metadata['current_metadata']
        current_column_names = current_metadata['column_names']

        report = {
            'date': self._inference_period,
            'model_package': self._model_package,
            'data_contract': self._contract_name,
            'row_cnt_diff': row_cnt_diff,
            'schema': {
                'summary': {
                    'healthy': number_of_columns_in_reference,
                    'critical': 0 if current_column_names == reference_column_names else 1
                }
            }
        }

        return report