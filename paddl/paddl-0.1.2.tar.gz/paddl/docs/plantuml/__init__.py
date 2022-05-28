from paddl.models import Table, Schema


HEADER = """
@startuml
  skinparam linetype ortho
  skinparam packageStyle rectangle
  skinparam shadowing false
  skinparam class {
    BackgroundColor White
    BorderColor Black
    ArrowColor Black
  }
  hide circle

"""
FOOTER = "\n@enduml\n"


def table(t: Table):
    columns = "\n".join([f"- {c.type.value} {c.name}" for c in t.columns])
    return f"class {t.name} {{\n{columns}\n}}"


def render(s: Schema):
    return HEADER +\
           "\n".join(map(table, s.tables)) +\
        FOOTER
