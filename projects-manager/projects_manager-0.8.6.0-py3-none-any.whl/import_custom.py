from asyncore import write
from pmanager.res import*
from os import path
from shutil import copyfile
from subprocess import run


def import_custom_module(namespace):

    pwarn("To know how to design your custom projects module, please refer you to : \nhttps://www.github.com/ThaaoBlues/pmanager/blob/main/README.MD")

    module_name = input("module name : \n-->")

    # make sure this module does not exists
    if path.exists(f"pmanager/modules/{module_name}.py"):
        perror(
            f"this projects module already exists, use \"pmanager edit_module {module_name}\" to edit his files")
        return

    while True:

        c = input(
            "1: Let pmanager pre-fill the module's files for you and open it in your ide to finish creation.\n2: directly give pmanager a path to the two files so it can copy it into its own folder.\n-->")

        if c == "1":
            pre_fill_module_files(module_name)
            with open("config/default_ide.conf", "r") as f:
                cmd = f.read() + \
                    f" \"pmanager/modules/{module_name}.xml\" \"pmanager/modules/{module_name}.py\""
                f.close()
                pinfo(f"running :\n{cmd}")
                run(cmd, shell=True)

            return

        elif c == "2":
            module_script_path = input("module script path (.py) \n-->")
            module_xml_path = input(
                "module files/folder architecture path (.xml) \n-->")

            pinfo("copying files")

            if path.exists(module_script_path) and path.exists(module_xml_path):
                copyfile(module_script_path,
                         f"pmanager/modules/{module_name}.py")
                copyfile(module_xml_path,
                         f"pmanager/modules/{module_name}.xml")
                psuccess(f"new module {module_name} added !")
            else:
                perror(
                    "one or the two path are invalid. (file not exists or you must have forgot a letter)")

            return

        else:
            pwarn("Invalid choice.")
