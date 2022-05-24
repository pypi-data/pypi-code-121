import os
import numpy as np
from workspace import env, git, message, cmake

name = "graph"
help = """Show the dependency graph"""
usage = ""
min_args = 0
colors = {}


def color(vendor):
    global colors

    if vendor not in colors:
        r, g, b = np.random.randint(100, 255, 3)
        colors[vendor] = "#%02X%02X%02X" % (r, g, b)

    return colors[vendor]


def run(args):
    graph = "digraph {\n"

    for directory in git.get_directories():
        parts = directory.split("/")
        vendor = parts[-2]
        project_name = "/".join(parts[-2:])
        graph += '"%s" [style=filled, color="%s"];\n' % (project_name, color(vendor))

        config = env.get_config(directory)
        if config and "deps" in config:
            for dep in config["deps"]:
                infos = git.parse_repository_name(dep)
                dep_name = "%s/%s" % (infos["vendor"], infos["name"])
                graph += '"%s" -> "%s";\n' % (project_name, dep_name)

    graph += "}\n"

    f = open("/tmp/deps.dot", "w")
    f.write(graph)
    f.close()

    os.system("dot -Tpng /tmp/deps.dot > /tmp/deps.png")
    os.system("eog /tmp/deps.png")
