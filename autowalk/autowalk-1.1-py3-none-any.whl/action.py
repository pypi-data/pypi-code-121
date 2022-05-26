#!/usr/bin/python

import re
import argparse
import subprocess as sp
from pathlib import Path
from importlib import  import_module

from utils.color import C
from config import CONFIG

class BaseAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):

        # delete -- , but this will cause you can't pass -- in add_argument
        option_strings = option_strings[0:1]

        super(BaseAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

        self.map_dict = {}
        self.dirs_list = []
        self.dup_set = set()
        self.path_set = set()
        self.PINYIN= False

    def __call__(self, parser, namespace, values, option_string=None):
        self._common_action()
        parser.exit()

    def _common_action(self):
        ...


    def _judge_prefix(self,t_dir):
        return  sum ( str( t_dir.name ).startswith(p) for p in CONFIG.GLOBAL_CONFIG.black_list_dirname_prefix) 

    def _check_config(self, file_option, default_path_name, check=True):
        try:
            # namedtuple
            path_name = getattr( CONFIG.GLOBAL_CONFIG, file_option)[0]
        except:
            path_name = Path.home() / f"{default_path_name}"
            print(C.red("[Warning]"))
            print(C.red(f'\t you not set your autojump config path in {C.green("~/.autowalk.py")}'))

            msg = f"~/{default_path_name}"
            print(C.red(f'\t guess and automatically set the path name to {C.green(msg)}'))

        if str(path_name).startswith("~"):
            path_name = Path.home().joinpath(path_name[2:])

        path = Path(path_name)
        if check:
            if path.exists():
                return path
            else:
                print(C.red("[AutoJump or File Not Found]"))
                notice = f"{C.purple(str(path))}"
                print(C.red(f"\t check your autojump config file: {notice}"))
                exit(-1)
        else:
            return path

    def _check_ranger_config(self):
        return self._check_config(
            file_option = "ranger_remap_output_file",  # DEFAULT_CONFIG's key in config.py
            default_path_name = ".rc_remap.conf",
            check=False
        )

    def _check_autojump_config(self):
        return self._check_config(
            file_option = "autojump_default_config",   # DEFAULT_CONFIG's key in config.py 
            default_path_name = ".local/share/autojump/autojump.txt"
        )

    def _deal_dependency(self, module_name):
        from importlib import  import_module
        try:
            return import_module(module_name)
        except Exception as e:
            print(C.red("[Dependency]"))

            notice = f"{C.purple(module_name)}"
            print(C.red(f"\t Module Not Found : {notice} "))

            tips = C.green(f"pip install {module_name}")
            print(C.red(f"\t Maybe you can try: {tips}"))
            exit(-1)

    def _collect(self, temp_dir):
        path_name = str( temp_dir )
        if path_name in self.path_set:
            pass
        else:
            self.path_set.add( path_name )
            dir_name = temp_dir.name.lower()
            if dir_name in self.dup_set:
                if self.PINYIN:
                    p = self._deal_dependency("pypinyin")
                    file_name = "".join(p.lazy_pinyin( f'{dir_name}-{temp_dir.parent.name}' ))
                else:
                    file_name = f'{dir_name}-{temp_dir.parent.name}'
            else:
                self.dup_set.add( dir_name )
                if self.PINYIN:
                    p = self._deal_dependency("pypinyin")
                    file_name = "".join(p.lazy_pinyin(dir_name))
                else:
                    file_name = dir_name

            map_str = f'map' \
                      f' ' \
                      f'{CONFIG.GLOBAL_CONFIG.prefix_and_suffix_only_for_ranger[0]}' \
                      f'{file_name}' \
                      f'{CONFIG.GLOBAL_CONFIG.prefix_and_suffix_only_for_ranger[1]}' \
                      f' ' \
                      f'cd' \
                      f' ' \
                      f'{path_name}'

            self.map_dict[map_str] = file_name         
            self.dirs_list.append( path_name )

    def _generate(self, path_obj_list, depth=0):
        if depth > int(CONFIG.GLOBAL_CONFIG.recursion_depth[0]):
            return
        else:
            for per_dir in path_obj_list:
                try:
                    if per_dir.is_dir() and str(per_dir.name) not in CONFIG.GLOBAL_CONFIG.black_list_dirname and  self._judge_prefix(per_dir)==0:
                        self._collect(per_dir)
                        self._generate( list(per_dir.iterdir()), depth+1)
                except PermissionError:
                    ...

    def check_autojump_install(self, cmd_str):
        try:
            result = sp.run(
                cmd_str,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
                shell=True, 
                # change the output of stderr and stdout from bytes to string
                universal_newlines=True, 
                # and must disabled encoding="utf-8" avoid coding err that can't try handle
                # encoding="utf-8",    
                check=True,
            )
            return result
        except:
            print(C.red("[AutoJump Not Found]"))
            notice = f"{C.purple('autojump')}"
            print(C.red(f"\t the option is for: {notice}, had you installed it?"))
            exit(-1)

    def generate(self):
        path_obj_list = [Path(d) for d in CONFIG.GLOBAL_CONFIG.recursion_root_list]
        self._generate(path_obj_list, depth=0)

    def append_default_and_print(self,):
        self.map_dict.update({}.fromkeys(CONFIG.GLOBAL_CONFIG.default_map_only_for_ranger))
        for map_str in self.map_dict.keys():
            print(map_str)
        print()

    def append_default_and_to_file(self,):
        self.map_dict.update({}.fromkeys(CONFIG.GLOBAL_CONFIG.default_map_only_for_ranger))
        ranger_path = self._check_ranger_config()
        ranger_path.write_text( "\n".join(self.map_dict.keys())+"\n")
        print(C.purple("[Write Completed]"))
        info = C.green(f"cat {ranger_path}")
        print(C.purple(f'\tcheck it: {info}'))

class CatConfigFile(BaseAction):
    def _common_action(self):
        print((Path.home() / ".autowalk.py").read_text())

class RemoveConfigAction(BaseAction):
    def _common_action(self):
        config_path = (Path.home() / f'{CONFIG.CONFIG_NAME}')
        if config_path.exists() and config_path.name == ".autowalk.py":
            config_path.unlink()

            print(C.purple("[Delete Completed]"))
            info = C.green(f"cat {config_path}")
            print(C.purple(f'\tcheck it: {info}'))

            msg = C.green("aw -h")
            print(C.purple(f'\tprompt  : use {msg} can recreate config file'))
            print()

class RangerAction(BaseAction):
    def _common_action(self):
        self.generate()
        self.append_default_and_print()

class RangerFileAction(BaseAction):
    def _common_action(self):
        self.generate()
        self.append_default_and_to_file()

class RangerPinAction(BaseAction):
    def _common_action(self):
        self.PINYIN = True # Just For CN
        self.generate()
        self.append_default_and_print()

class RangerPinFileAction(BaseAction):
    def _common_action(self):
        self.PINYIN = True # Just For CN
        self.generate()
        self.append_default_and_to_file()




class JumpBase(BaseAction):
    def _common_action(self):
        self.generate()

        # if self._async:
        #     # import asyncio
        #     # from multiprocessing import cpu_count
        #     # from concurrent.futures import ThreadPoolExecutor
        #     # async def async_run(async_cmd):
        #     #     await asyncio.create_subprocess_shell(async_cmd,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)     
        #     # async def main():
        #     #     async_run_list = [] 
        #     #     for file in self.dirs_list:
        #     #         auto_jump_cmd = f'cd "{file}" && autojump -a "{file}" && autojump -i {CONFIG.GLOBAL_CONFIG.weight_value_only_for_autojump[0]}'
        #     #         async_run_list.append( async_run(auto_jump_cmd) )
        #     #     await asyncio.gather( *async_run_list )
        #     # asyncio.run(main())
        #     ###############################################################
        #     # loop = asyncio.get_event_loop()
        #     # executor = ThreadPoolExecutor( cpu_count() )
        #     # loop.set_default_executor(executor)
        #     # asyncio.get_event_loop().run_until_complete(main())
        #     # executor.shutdown(wait=True)
        #     # loop.close()
        #     ###############################################################
        #     # for _ in range(epoch):
        #     # for file in self.dirs_list:
        #     #     auto_jump_cmd = f'cd "{file}" && autojump -a "{file}" && autojump -i {CONFIG.GLOBAL_CONFIG.weight_value_only_for_autojump[0]}'
        #     #     sp.Popen(auto_jump_cmd,stdout=sp.PIPE,stderr=sp.PIPE,shell=True, encoding="utf-8")

        #     autojump_config_path = self._check_autojump_config()
        #     max_epoch = 5
        #     raw_set = set(self.dirs_list)

        #     for x in range(max_epoch):
        #         if not raw_set:
        #             break

        #         print(len(raw_set))
        #         # print(raw_set)
        #         for file in raw_set:
        #             auto_jump_cmd = f'cd "{file}" && autojump -a "{file}" && autojump -i {CONFIG.GLOBAL_CONFIG.weight_value_only_for_autojump[0]}'
        #             sp.Popen(auto_jump_cmd,stdout=sp.PIPE,stderr=sp.PIPE,shell=True, encoding="utf-8")

        #         with autojump_config_path.open() as f:
        #             raw_set -= {line.strip().split("\t")[1].strip() for line in set(f)}

        # else:
        #     for file in self.dirs_list:
        #         auto_jump_cmd = f'cd "{file}" && autojump -a "{file}" && autojump -i {CONFIG.GLOBAL_CONFIG.weight_value_only_for_autojump[0]}'


        #         result = sp.run(auto_jump_cmd,stdout=sp.PIPE,stderr=sp.PIPE,shell=True, encoding="utf-8")
        #         weight_filename = result.stdout.strip().split(":",1)

        #         final_print = f'\t{C.green(weight_filename[0])}{C.red(":")}{C.purple(weight_filename[1])}'
        #         print(final_print)

        aj_cnofig_path = self._check_autojump_config()
        dirs_set = set(self.dirs_list)
        user_define_weight = CONFIG.GLOBAL_CONFIG.weight_value_only_for_autojump[0]

        old_conf = aj_cnofig_path.read_text().strip()
        old_file_name_set = set()

        if not old_conf:
            aj_cnofig_path.write_text( "\n".join( f"{user_define_weight}\t{path_obj}" for path_obj in dirs_set)+"\n" )
        else:
            old_config_update_set = set()
            for line in old_conf.split("\n"):
                file_name = line.split("\t")[1]
                old_file_name_set.add(file_name)
                old_config_update_set.add (
                    str(float(line.split("\t")[0])+float(user_define_weight)) + "\t" + file_name
                )
            new_config_update_set = {f"{user_define_weight}\t{diff_name}" for diff_name in dirs_set - old_file_name_set}

            new_total_config = {*old_config_update_set,*new_config_update_set}
            aj_cnofig_path.write_text( "\n".join( new_total_config ) + "\n")

        print(C.purple("[Completed]"))
        print(C.purple(f'\tUse {C.green("aw -l")} to check show your weights'))
        print()


# class JumpSyncAction(JumpBase):
#     def _common_action(self):
#         self._async = False
#         super()._common_action()

# class JumpAsyncAction(JumpBase):
#     def _common_action(self):
#         self._async = True
#         super()._common_action()


class JumpListAction(JumpBase):
    def _common_action(self):
        auto_jump_cmd = "autojump -s"
        result = self.check_autojump_install(auto_jump_cmd)

        line_list = result.stdout.split("\n")
        print()

        mark = True
        for line in line_list:
            split_list = line.split(":",1)
            if len(split_list) > 1 and mark:
                print(f'\t\t{C.green(split_list[0])} {C.red("│".rjust(10-len(split_list[0])))}{C.purple(split_list[1].strip())}')
            else:
                mark = False
                if not split_list[0].strip():
                    pass
                elif "_" in split_list[0]:
                    print("\t" + C.red( int(len(split_list[0])/1.6) * "──" ))
                elif len(split_list) == 1:
                    print(C.green("\t"+line))
                else :
                    print(f'\t{C.purple(split_list[0])}{C.red("│".rjust(10-len(split_list[0])))}{C.green(split_list[1].strip())}')

        print()

class JumpClearAction(JumpBase):
    def find_autojump_config(self,):
        auto_jump_cmd = "autojump -s"
        result = self.check_autojump_install(auto_jump_cmd)
        result = result.stdout.split("\n")
        autojump_config_path = self._check_autojump_config()

        print(C.purple("[Cleared]"))
        if Path(autojump_config_path).exists():
            autojump_config_path.write_text("")
            cmd_str = C.green(f"cat {autojump_config_path}")
            cmd_str2 = C.green(f"aw -l")
            print(C.purple(f'\tUse command {cmd_str2} or {cmd_str} to check'))
            print()
        else:
            try:
                p2 = Path(result[-2].split(":")[1].strip())
                p2.write_text("")
                cmd_str = C.green(f"cat {p2}")
                cmd_str2 = C.green(f"aw -l")
                print(C.purple(f'\tUse command {cmd_str2} or {cmd_str} to check'))
                print()
            except Exception as e:
                print(C.red("No Config File Find !"))

    def _common_action(self):
        self.find_autojump_config()


class JumpJunkCleanAction(JumpBase):
    def _common_action(self):
        try:
            autojump_config_path = self._check_autojump_config()
            
            with autojump_config_path.open() as f_before:
                before_clean_line_set = set(f_before)

            auto_jump_cmd = "autojump --purge"
            self.check_autojump_install(auto_jump_cmd)
            print(C.purple("[Cleaned Junk]"))    

            with autojump_config_path.open() as f_after:
                after_clean_line_set = set(f_after)

            cleaned_set = before_clean_line_set - after_clean_line_set
            count = len(cleaned_set)
            if count == 0:
                print(f'\t{C.green("Nothing to clean up")}')         
            else:
                print(f'\t{C.red("─" * 55)}')
                for line in cleaned_set:
                    weight, file_name = line.strip().split("\t")

                    cleaned_item = f'{int(float( weight.strip()))}{C.red("│")} {file_name.strip()}'
                    print(f"\t\t{cleaned_item}")
                print(f'\t{C.red("─" * 55)}')
                print(f'\t{C.purple("total cleaned")}{C.red("│")} {C.green(count)}')
                print(f'\t{C.purple("weight config")}{C.red("│")} {C.green(autojump_config_path.resolve())}')
        except:
            auto_jump_cmd = "autojump --purge"
            result = self.check_autojump_install(auto_jump_cmd)
            print("\t"+C.purple(result.stdout))


class BaseArgsCommon:
    def check_autojump_install_for_args_action(self, *args, **kwargs):
        input_path_name = ""
        try:
            input_path_name = kwargs["file"] 
            auto_jump_cmd = args[0]
            result = sp.run(
                auto_jump_cmd,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
                shell=True, 
                # change the output of stderr and stdout from bytes to string
                universal_newlines=True, 
                # and must disabled encoding="utf-8" avoid coding err that can't try handle
                # encoding="utf-8",    
                check=True,
            )

            weight_filename = result.stdout.strip().split(":",1)
            final_print = f'\t{C.green(weight_filename[0])}{C.red(":")}{C.purple(weight_filename[1])}'
            print(C.purple("[INCR COMPLETED]"))
            print(final_print)
            print()
        except:
            print(C.red("[AutoJump or Directory Not Found]"))
            notice = C.purple( "autojump" )
            print(C.red(f"\t 1. the option is for: { notice }, had you installed it?"))
            print(C.red(f"\t 2. check your input path: {C.purple(input_path_name)}"))
            # parser.print_help()

class IncrWeightAction(argparse._StoreAction, BaseArgsCommon):
    def __call__(self, parser, args, values, option_string=None):
        file, weight = values
        auto_jump_cmd = f'cd "{file}" && autojump -a "{file}" && autojump -i {weight}'
        self.check_autojump_install_for_args_action(auto_jump_cmd, file=file)

class DecrWeightAction(argparse._StoreAction, BaseArgsCommon):
    def __call__(self, parser, args, values, option_string=None):    
        file, weight = values
        auto_jump_cmd = f'cd "{file}" && autojump -a "{file}" && autojump -d {weight}'
        self.check_autojump_install_for_args_action(auto_jump_cmd, file=file)