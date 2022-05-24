import re
import traceback
from texttable import Texttable


def draw_table(backend, command, result, columns, extra={}):

    # Now we have to beautify
    data = result["data"]

    t = Texttable(max_width=0)
    t.add_rows(
        [
            ["Attribute", "Value"],
            ["Name", backend.config["name"]],
            ["Server", backend.config["server"]],
            ["Command", command],
        ]
        + [[k, v] for k, v in extra.items()]
    )
    print(t.draw())

    t = Texttable(max_width=0)
    # t.set_deco(Texttable.HEADER)
    t.add_rows([columns] + [[d.get(c, "") for c in columns] for d in data])

    print(t.draw())


def draw(backend, command, result, columns, extra={}):
    return draw_table(backend, command, result, columns, extra)


def draw_dict(backend, command, result, keys, extra={}):

    # Now we have to beautify
    data = result["data"]

    t = Texttable(max_width=0)
    t.add_rows(
        [
            ["Attribute", "Value"],
            ["Name", backend.config["name"]],
            ["Server", backend.config["server"]],
            ["Command", command],
        ]
        + [[k, v] for k, v in extra.items()]
    )
    print(t.draw())

    t = Texttable(max_width=0)
    # t.set_deco(Texttable.HEADER)
    t.add_rows([["Key", "Value"]] + [[c, data.get(c, "")] for c in keys])

    print(t.draw())


def draw_run_detail(backend, command, result, extra={}):

    # Now we have to beautify
    data = result["data"]

    t = Texttable(max_width=0)
    t.add_rows(
        [
            ["Attribute", "Value"],
            ["Name", backend.config["name"]],
            ["Server", backend.config["server"]],
            ["Command", command],
        ]
        + [[k, v] for k, v in extra.items()]
    )
    print(t.draw())
    print("\n")

    if "metadata" not in data:
        return

    metadata = data["metadata"]

    print("RUN DETAILS")

    rows = [
        ["Attribute", "Value"],
        ["Start", metadata["start_time"]],
        ["End", metadata.get("end_time", "")],
        ["Command", " \n".join(metadata["cmdline"])],
        ["User", metadata["stats"]["user"]],
        ["Host", metadata["stats"]["platform"]["node"]],
    ]

    notes = metadata.get("summary", []) + metadata.get("performance_summary", [])
    if len(notes) > 0:
        rows.append(["Summary", "\n".join(notes)])

    t = Texttable(max_width=0)
    t.add_rows(rows)
    print(t.draw())
    print("\n")

    print("OUTPUTS")

    rows = [["Frame", "Type", "Description", "Size", "Path"]]
    for name, details in metadata.get("details", {}).items():
        frametype = details["frametype"]
        description = ""
        path = ""
        filesize = ""
        params = details.get("params", {})
        for p in params:
            if p.get("action", None) != "output":
                continue

            description = p.get("descriptions", p.get("description", ""))
            if isinstance(description, list):
                description = [d[:30] for d in description]
                description = "\n".join(description)
            else:
                description = description[:30]
            components = p.get("components", [])
            if len(components) > 0:
                path = "..." + components[0]["filename"][-30:]
                filesize = components[0]["filesize"]
            break
        rows.append([name, frametype, description, filesize, path])

    t = Texttable(max_width=0)
    t.add_rows(rows)
    print(t.draw())
    print("\n")

    print("VERSIONS")

    rows = [["Label", "Description", "Release", "Commit"]]
    for v in metadata["versionmap"]:
        repo = v["repo"]
        label = v["label"]
        commit = v["commit"][:8]
        description = v["description"][:20]
        release = v["release"]
        if repo.startswith("scribble-"):
            continue
        rows.append([label, description, release, commit])
    t = Texttable(max_width=0)
    t.add_rows(rows)
    print(t.draw())
    print("\n")

    if "process" in metadata:
        print("RESOURCES")
        rows = [["Attribute", "Value"]]
        for v in metadata["process"]:
            if v[0] in ["VmPeak", "VmSize", "MemTotal", "MemFree"]:
                rows.append(v)
        t = Texttable(max_width=0)
        t.add_rows(rows)
        print(t.draw())
        print("\n")

    print("LOG")
    log = data["log"]
    rows = [["Elapsed", "Transform", "Level", "Message"]]
    for l in log:
        try:
            rows.append(
                [
                    l["elapsed"],
                    l.get("transform", ""),
                    l["levelname"],
                    l["message"][:30],
                ]
            )
        except:
            traceback.print_exc()
    t = Texttable(max_width=0)
    t.add_rows(rows)
    print(t.draw())


def draw_health(backend, command, result, extra={}):

    # Now we have to beautify
    data = result["data"]

    def fixedlength(paragraph, n):
        paragraph = paragraph.strip()
        return "\n".join([paragraph[i : i + n] for i in range(0, len(paragraph), n)])

    for section in data:
        print(section["title"])
        print("-----")
        print(section["description"])
        t = Texttable(max_width=0)
        rows = [["Option", "Value", "Description"]]
        for o in section["options"]:
            value = o["value"]
            value = value.replace("<br>", "\n")
            value = value.replace("</th>\n", "</th>")
            value = value.replace("</td>\n", "</td>")
            value = re.sub("<[^>]+>", "", value)
            name = fixedlength(o["name"], 20)
            desc = fixedlength(o["description"], 20)
            rows.append([name, desc, value])
        t.add_rows(rows)
        print(t.draw())
        print("\n")
