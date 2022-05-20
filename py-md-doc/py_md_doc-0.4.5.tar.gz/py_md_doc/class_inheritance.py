import re
import importlib
from pathlib import Path
from typing import List, Union, Dict, Type
from py_md_doc.py_md_doc import PyMdDoc


class ClassInheritance:
    """
    Handle documentation with class inheritance.
    """

    @staticmethod
    def get_from_directory(input_directory: Union[str, Path], output_directory: Union[str, Path], import_path: str,
                           overrides: Dict[str, str] = None, import_prefix: str = None,
                           excludes: List[str] = None, includes: List[str] = None) -> None:
        """
        Generate documentation with class inheritance from a source directory.
        This assumes that:

        1. The entire hierarchy is in the same directory; anything outside of it will be ignored.
        2. Each .py file is named with underscore snake casing and contains an uppercase camelcase class name, for example `my_class.py` and `MyClass`.

        :param input_directory: The input source directory of .py scripts.
        :param output_directory: The output destination directory of .md files.
        :param import_path: The expected Python import path, for example `module.sub_module`.
        :param overrides: Override any unexpected classes or filenames. Key = What would be programatically expected such as `MyClass`. Value = What actually exists such as `MYCLASS`.
        :param import_prefix: The import prefrix, for example `from module.sub_module`.
        :param excludes: Exclude any .py in this list.
        :param includes: If not None, only include these .py files.
        """

        if isinstance(input_directory, Path):
            src_dir = input_directory
        elif isinstance(input_directory, str):
            src_dir = Path(input_directory)
        else:
            raise TypeError(f"Invalid directory type for {input_directory}")
        if isinstance(output_directory, Path):
            dst_dir = output_directory
        elif isinstance(output_directory, str):
            dst_dir = Path(output_directory)
        else:
            raise TypeError(f"Invalid directory type for {output_directory}")
        # Create child docs.
        files = []
        for f in input_directory.iterdir():
            if f.is_dir() or f.suffix != ".py" or (excludes is not None and f.name in excludes) or (includes is not None and f.name not in includes):
                continue
            files.append(str(f.resolve()))
        PyMdDoc(input_directory=src_dir, files=files).get_docs(output_directory=output_directory,
                                                               import_prefix=import_prefix)
        # Create inheritance docs from the child docs.
        for f in src_dir.iterdir():
            if f.is_file() and f.suffix == ".py" and (excludes is None or f.name not in excludes) and (includes is None or f.name in includes):
                class_name = ''.join(x.capitalize() or '_' for x in f.name[:-3].split('_'))
                if overrides is not None and class_name in overrides:
                    class_name = overrides[class_name]
                doc = ClassInheritance.get_from_type(
                    t=getattr(importlib.import_module(f"{import_path}.{f.name[:-3]}"), class_name),
                    directory=dst_dir,
                    overrides=overrides)
                dst_dir.joinpath(f.name[:-3] + ".md").write_text(doc)

    @staticmethod
    def get_from_type(t: Type, directory: Union[str, Path], overrides: Dict[str, str] = None) -> str:
        """
        Generate documentation with class inheritance from a source type and documentation directory.

        This assumes that:

        1. Documentation without inheritance has already been generated (see `PyMdDoc.get_docs()`).
        2. Type `t` is one of the classes in the .md `directory`.

        :param t: The class type.
        :param directory: The directory of output .md files that have already been generated.
        :param overrides: Override any unexpected classes or filenames. Key = What would be programatically expected such as `MyClass`. Value = What actually exists such as `MYCLASS`.

        :return: Documentation text.
        """

        if isinstance(directory, Path):
            rd = directory
        elif isinstance(directory, str):
            rd = Path(directory)
        else:
            raise TypeError(f"Invalid directory type for {directory}")
        hierarchy = list(t.__mro__)
        class_name = ClassInheritance._camel_case_to_underscore(hierarchy[0].__name__)
        if overrides is not None and class_name in overrides:
            class_name = overrides[class_name]
        child_text = rd.joinpath(class_name + ".md").read_text(encoding="utf-8")
        parent_texts = []
        for i in range(1, len(hierarchy)):
            class_name = ClassInheritance._camel_case_to_underscore(hierarchy[i].__name__)
            if overrides is not None and class_name in overrides:
                class_name = overrides[class_name]
            parent_path = rd.joinpath(class_name + ".md")
            if not parent_path.exists():
                break
            parent_texts.append(parent_path.read_text(encoding="utf-8"))
        return ClassInheritance.get_from_text(child_text=child_text, parent_texts=parent_texts)

    @staticmethod
    def get_from_text(child_text: str, parent_texts: List[str]) -> str:
        """
        Generate documentation with inheritance from parent documentation.

        :param child_text: The documentation of the child class.
        :param parent_texts: A list of documentation of the parent classes in order of inheritance.

        :return: An updated version of `child_text` that includes class inheritance.
        """

        re_class_name = r'^# (.*)'
        child_class_name = re.search(re_class_name, child_text, flags=re.MULTILINE).group(1)
        # Get class variables.
        class_variables = []
        re_class_variables = r'^## Class Variables\n\n(.*)\n(.*)\n((.|\n)*?)(\*\*\*|\Z)'
        for parent_text in parent_texts:
            parent_class_variables_search = re.search(re_class_variables, parent_text, flags=re.MULTILINE)
            if parent_class_variables_search is not None:
                class_variables.extend(parent_class_variables_search.group(3).strip().split("\n"))
        child_class_variables_search = re.search(re_class_variables, child_text, flags=re.MULTILINE)
        if child_class_variables_search is not None:
            class_variables.extend(child_class_variables_search.group(3).strip().split("\n"))
        class_variables = list(sorted(set(class_variables)))
        if len(class_variables) > 0:
            class_variables_text = "## Class Variables\n\n| Variable | Type | Description | Value |\n| --- | --- | --- | --- |\n" + "\n".join(class_variables)
            if "## Class Variables" in child_text:
                child_text = re.sub(re_class_variables, class_variables_text, child_text, flags=re.MULTILINE)
            else:
                split = child_text.split("***")
                # Add a section at the end of the document.
                if len(split) == 1:
                    child_text += f"\n\n***\n\n{class_variables_text}"
                # Add a section between the header and the next section.
                else:
                    child_text = child_text.replace(split[0], split[0].strip() + f"\n\n{class_variables_text.strip()}\n\n").strip()
        # Get fields.
        parent_fields = []
        re_fields = r'^## Fields((.|\n)*?)(\*\*\*|\Z)'
        re_field = r'^(- (.*?)$)'
        for parent_text in parent_texts:
            parent_fields_search = re.search(re_fields, parent_text, flags=re.MULTILINE)
            if parent_fields_search is not None:
                pf = re.findall(re_field, parent_fields_search.group(1).strip(), flags=re.MULTILINE)
                parent_fields.extend([q[0] for q in pf])
        if len(parent_fields) > 0:
            parent_fields_text = "\n\n".join(parent_fields)
            if "## Fields" not in child_text:
                split = child_text.split("***")
                # Add a section at the end of the document.
                if len(split) == 1:
                    child_text = child_text.strip() + "\n\n***\n\n## Fields\n\n" + parent_fields_text + "\n\n***\n\n"
                # Add a section between the header and the next section.
                else:
                    child_text = child_text.replace(split[0], split[0].strip() + "\n\n***\n\n## Fields\n\n" + parent_fields_text + "\n\n***\n\n")
            # Append fields.
            else:
                child_fields_text = re.search(re_fields, child_text, flags=re.MULTILINE).group(1)
                cf = re.findall(re_field, child_fields_text.strip(), flags=re.MULTILINE)
                fields = [q[0] for q in cf]
                fields.extend(parent_fields)
                child_text = child_text.replace(child_fields_text, "\n\n" + "\n\n".join(fields) + "\n\n").strip()
        # Get the __init__ function.
        init = None
        re_init = r'## Functions\n\n#### (\\_\\_init\\_\\_((.|\n)*?))(^#|\Z)'
        child_init_search = re.search(re_init, child_text, flags=re.MULTILINE)
        parent_class_names = []
        for parent_text in parent_texts:
            parent_class_name = re.search(re_class_name, parent_text, flags=re.MULTILINE).group(1)
            parent_class_names.append(parent_class_name)
        if child_init_search is None:
            for parent_text in parent_texts:
                parent_init_search = re.search(re_init, parent_text, flags=re.MULTILINE)
                if parent_init_search is not None:
                    # Replace the class name.
                    init = parent_init_search.group(1)
                    break
        if init is None:
            init = f'\\_\\_init\\_\\_\n\n**`{child_class_name}()`**'
        else:
            init = init.strip()
        # The first function.
        functions = {"\\_\\_init\\_\\_": init}
        re_functions = r'^## Functions((.|\n)*?)(\*\*\*|\Z)'
        re_function = r'^#### (.*)((.|\n)*?)(?=^#|\Z)'
        for parent_text in parent_texts:
            parent_functions_search = re.search(re_functions, parent_text, flags=re.MULTILINE)
            if parent_functions_search is not None:
                pf = re.findall(re_function, parent_functions_search.group(1).strip(), flags=re.MULTILINE)
                for fn in pf:
                    # Ignore anything lacking a docstring.
                    if fn[0] in functions or fn[1].strip()[-1] == "*":
                        continue
                    functions[fn[0]] = fn[1].strip()
        child_functions_search = re.search(re_functions, child_text, flags=re.MULTILINE)
        if child_functions_search is not None:
            pf = re.findall(re_function, child_functions_search.group(1).strip(), flags=re.MULTILINE)
            for fn in pf:
                # Ignore anything lacking a docstring.
                if fn[1].strip()[-1] == "*":
                    continue
                functions[fn[0]] = fn[1].strip()
        function_text = "\n\n".join([f"#### {k}\n\n{v}" for k, v in functions.items()])
        # Append the functions.
        if "## Functions" in child_text:
            child_text = re.sub(re_functions, f"## Functions\n\n{function_text}", child_text, flags=re.MULTILINE)
        # Create a new section.
        else:
            child_text = child_text.strip() + f"\n\n***\n\n## Functions\n\n{function_text}"
        child_text = child_text.replace("***\n\n***", "***")
        for parent_class_name in parent_class_names:
            child_text = child_text.replace(parent_class_name + "(", child_class_name + "(")
            child_text = child_text.replace(f"{child_class_name}({parent_class_name})", child_class_name)
        section_break_fields = "***\n\n## Fields"
        section_break_functions = "***\n\n## Functions"
        if "## Class Variables" in child_text:
            if "## Fields" in child_text and section_break_fields not in child_text:
                child_text = child_text.replace("## Fields", section_break_fields)
            elif "## Functions" in child_text and section_break_functions not in child_text:
                child_text = child_text.replace("## Functions", section_break_functions)
        child_text = child_text.replace(f"{child_class_name}(ABC)", child_class_name)
        return child_text

    @staticmethod
    def _camel_case_to_underscore(text: str) -> str:
        # Source: https://stackoverflow.com/a/1176023
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
