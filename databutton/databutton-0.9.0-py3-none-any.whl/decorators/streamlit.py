import inspect
import os
from dataclasses import dataclass
from typing import List, Optional

# Decorator for defining a method as a streamlit app


DEFAULT_MEMORY = "256Mi"
DEFAULT_CPU = "0.2"


@dataclass
class StreamlitApp:
    filename: str
    uid: str
    name: str
    route: str
    memory: str = DEFAULT_MEMORY
    cpu: str = DEFAULT_CPU
    port: int = 0


# Global var to store all streamlit apps
_streamlit_apps: List[StreamlitApp] = []


def streamlit(
    route: str,
    name: str = None,
    memory: Optional[str] = None,
    cpu: Optional[str] = None,
):
    def app(func):
        cleaned_route = route if route.endswith("/") else route + "/"
        splitted_route = list(filter(None, cleaned_route.split("/")))
        uid = "-".join(splitted_route)
        filename = "./.databutton/app/tmp-" + uid + ".py"
        if os.path.exists("./.databutton/app") is False:
            os.makedirs("./.databutton/app")

        module_name = inspect.getmodule(func).__name__
        func_name = func.__name__
        import_statement = f"from {module_name} import {func_name}"

        with open(filename, "w") as f:
            f.write(import_statement)
            f.write("\n")
            f.write("\n")
            f.write(f"{func_name}()")
        st = StreamlitApp(
            filename=filename,
            route=cleaned_route,
            name=name if name else func_name,
            uid=uid,
        )
        if memory:
            st.memory = memory
        if cpu:
            st.cpu = cpu
        _streamlit_apps.append(st)
        return func

    return app
