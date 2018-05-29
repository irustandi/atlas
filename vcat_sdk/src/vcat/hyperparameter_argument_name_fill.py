from vcat.hyperparameter import Hyperparameter


class HyperparameterArgumentNameFill(object):

    def fill_arg_template(self, new_args, arg, kwargs):
        if isinstance(arg, Hyperparameter):
            arg_display = kwargs.get(arg.name, "<using default>")
            new_args.append({"hyperparameter_value": arg_display,
                             "hyperparameter_name": arg.name})
            return True
        return False

    def fill_kwarg_template(self, new_kwargs, keyword, arg, kwargs):
        if isinstance(arg, Hyperparameter):
            kwarg_display = kwargs.get(keyword, "<using default>")
            new_kwargs[keyword] = {
                "hyperparameter_value": kwarg_display, "hyperparameter_name": keyword}
            return True
        return False