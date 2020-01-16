envsubst '$FOUNDATIONS_HOME $LOCAL_DOCKER_SCHEDULER_HOST' < acceptance/v2beta/fixtures/foundations_home/config/local_docker_scheduler/worker_config/submission/scheduler.config.envsubst.yaml > acceptance/v2beta/fixtures/foundations_home/config/local_docker_scheduler/worker_config/submission/scheduler.config.yaml
envsubst '$REMOTE_FOUNDATIONS_HOME $LOCAL_DOCKER_SCHEDULER_HOST $REDIS_PORT' < acceptance/v2beta/fixtures/foundations_home/config/submission/scheduler.config.envsubst.yaml > acceptance/v2beta/fixtures/foundations_home/config/submission/scheduler.config.yaml

envsubst '$FOUNDATIONS_HOME $REDIS_HOST' < acceptance/v2beta/fixtures/foundations_home/config/local_docker_scheduler/worker_config/execution/default.config.envsubst.yaml > acceptance/v2beta/fixtures/foundations_home/config/local_docker_scheduler/worker_config/execution/default.config.yaml
envsubst '$FOUNDATIONS_HOME $LOCAL_DOCKER_SCHEDULER_HOST $REDIS_PORT' < acceptance/v2beta/fixtures/foundations_home/config/execution/default.config.envsubst.yaml > acceptance/v2beta/fixtures/foundations_home/config/execution/default.config.yaml

envsubst '$REDIS_HOST $REDIS_PORT' < acceptance/v2beta/fixtures/foundations_home/config/local_docker_scheduler/database.config.envsubst.yaml > acceptance/v2beta/fixtures/foundations_home/config/local_docker_scheduler/database.config.yaml
envsubst '$REDIS_HOST $REDIS_PORT' < acceptance/v2beta/fixtures/foundations_home/config/local_docker_scheduler/tracker_client_plugins.envsubst.yaml > acceptance/v2beta/fixtures/foundations_home/config/local_docker_scheduler/tracker_client_plugins.yaml