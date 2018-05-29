from vcat.stage_graph import StageGraph
from vcat.stage_piping import StagePiping
from vcat.stage_smart_constructor import StageSmartConstructor
from vcat.stage_connector_wrapper import StageConnectorWrapper
from vcat.stage_context import StageContext
from vcat.context_aware import ContextAware

class Pipeline(object):

    def __init__(self, pipeline_context):
        self.graph = StageGraph()
        self.pipeline_context = pipeline_context
        self._stage_piping = StagePiping(self)

    def stage(self, function, *args, **kwargs):
        new_context = StageContext()
        stage_smart_constructor = StageSmartConstructor(new_context)

        if isinstance(function, ContextAware):
            function._set_context(new_context)

        current_stage = stage_smart_constructor.make_stage(
            new_context, function, *args, **kwargs)
        return StageConnectorWrapper(self.graph.stage(current_stage), self.pipeline_context, new_context)

    def join(self, upstream_connector_wrappers, function, *args, **kwargs):
        upstream_connectors = [
            wrapper._connector for wrapper in upstream_connector_wrappers]

        new_context = StageContext()
        stage_smart_constructor = StageSmartConstructor(new_context)
        current_stage = stage_smart_constructor.make_stage(
            new_context, function, *args, **kwargs)
        return StageConnectorWrapper(self.graph.join(current_stage, upstream_connectors), self.pipeline_context, new_context)

    def __or__(self, stage_args):
        return self._stage_piping.pipe(stage_args)
