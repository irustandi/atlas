#!/bin/bash
cwd=`pwd`
echo Uploading modules via user $NEXUS_USER

twine upload -u jenkins-user -p $NEXUS_PASSWORD --repository-url $NEXUS_URL ${cwd}/dist/*.whl