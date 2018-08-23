"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""

"""
If you haven't seen the "replacing_nulls" or "one_hot_encode" modules yet, have a look
at one of those before you look at this one.

This is structured in much the same way as those other two modules, but there's a key
difference - there's a .splice() method.  Due to the fact that Python is dynamically typed,
among other things, Foundations simply cannot know how many values a stage returns when
wrapping it.  You'll need to help just a little bit by calling the splice method.

The usage is simple enough - do stage.splice(n) if the stage wants to return n elements to
other stages.  See lines 36 - 40 in this file for examples of usage.
"""

import foundations
import config
from staged_common.prep import union
from staged_common.models import train_logistic_regression
from staged_common.logging import log_formatted
from staged_titanic.etl import load_data, fill_categorical_nulls, split_inputs_and_targets, split_training_and_validation, impute, one_hot_encode, drop_non_numeric_columns, get_metrics


def main():
    # data prep
    data = load_data()
    data = fill_categorical_nulls(data)
    inputs, targets = split_inputs_and_targets(data).splice(2)

    # feature engineering
    x_train, x_valid, y_train, y_valid = split_training_and_validation(
        inputs, targets).splice(4)
    x_train, x_valid = impute(x_train, x_valid).splice(2)
    x_train, x_valid = one_hot_encode(x_train, x_valid).splice(2)
    x_train, x_valid = drop_non_numeric_columns(x_train, x_valid).splice(2)

    # model training and scoring
    model = train_logistic_regression(x_train, y_train)
    y_train, train_score = get_metrics(model, x_train, y_train, 'Training').splice(2)
    y_valid, valid_score = get_metrics(model, x_valid, y_valid, 'Validation').splice(2)
    results = union(y_train, y_valid)

    # print out the results
    log_formatted('\nData: {}\nTraining score was {}\nValidation score was {}',
                  results, train_score, valid_score).run()


if __name__ == '__main__':
    main()