"""
Copyright (C) DeepLearning Financial Technologies Inc. - All Rights Reserved
Unauthorized copying, distribution, reproduction, publication, use of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Thomas Rogers <t.rogers@dessa.com>, 06 2018
"""


class AppManager(object):
    """A class to manage the initilization of the Flask server.
        Arguments:
            
    """    
    def __init__(self):
        self._app = None

    def app(self):
        """Create and instantiate Flask object
        """
        from flask import Flask

        if self._app is None:
            self._app = Flask(__name__)

        return self._app