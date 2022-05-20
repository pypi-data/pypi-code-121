def get_function(jobs, routes, context):
    name = context.function_name
    fname = name.split("-")[-2]
    module = jobs if fname.startswith("Job") else routes
    name = fname.replace("Job", "").replace("Route", "")

    fn = getattr(module, _camel_to_snake(name))

    return fn


def _camel_to_snake(s):
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")
