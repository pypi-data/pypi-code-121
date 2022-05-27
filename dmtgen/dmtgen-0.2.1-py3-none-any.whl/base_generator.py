#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Base generator
'''

import os
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import Dict
import jinja2
from dmt.common.package import Package
from .package_generator import PackageGenerator
from .basic_template_generator import BasicTemplateGenerator
from .template_generator import TemplateBasedGenerator
from .template import escape_string


class BaseGenerator(PackageGenerator):
    """ Generates a Python runtime library to access the entities as plain objects """

    def __init__(self, root_dir: Path, package_name: str,
                 output_dir: Path, root_package: Package) -> None:
        self.package_name = package_name
        self.template_root = root_dir /"templates"
        self.output_dir = output_dir
        self.source_only = False
        self.root_package = root_package
        self.generators = self.get_template_generators()

    def get_template_generators(self) -> Dict[str,TemplateBasedGenerator]:
        """ Override in subclasses """
        return {}

    def generate_package(self, config: Dict):
        """ Generate package """
        self.source_only = config.get("source",self.source_only)
        self.__generate_from_templates(self.template_root, self.output_dir,config)


    def __generate_from_templates(self, template_root: Path, output_dir: Path, config: Dict):
        cleanup = config.get("cleanup",False)
        if cleanup and os.path.exists(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)

        self.copy_templates(template_root,output_dir)

        self.pre_generate(output_dir)

        self.__find_templates_and_generate(output_dir, config)

        self.post_generate(output_dir)

    def copy_templates(self, template_root: Path, output_dir: Path):
        """Copy template folder to output folder"""
        # First we copy the entire tree structure
        # Then we have the sceleton to convert the files afterwards
        copy_tree(str(template_root), str(output_dir))

    def pre_generate(self,output_dir: Path):
        """ override in subclass """

    def post_generate(self,output_dir: Path):
        """ override in subclass """

    def __find_templates_and_generate(self, output_dir: Path, config: Dict):
        for path in sorted(output_dir.rglob('*.jinja')):
            generator = self.generators.get(path.name,BasicTemplateGenerator())
            self.__generate_template(path, generator, config)

    @staticmethod
    def __read_template(templatefile: Path):
        loader = jinja2.FileSystemLoader(templatefile.parents[0])
        env_parameters = dict(
            loader=loader,
            undefined=jinja2.StrictUndefined
        )
        environment = jinja2.Environment(**env_parameters)
        environment.filters["escape_string"] = escape_string
        return environment.get_template(templatefile.name)

    def __generate_template(self, template_file: Path, template_generator: TemplateBasedGenerator, config: Dict):
        template = self.__read_template(template_file)
        file_name = self.__remove_suffix(template_file)
        outputfile = template_file.parents[0] / file_name

        template_generator.generate(self,template, outputfile, config)
        # Remove the copied placeholder
        os.remove(template_file)

    @staticmethod
    def __remove_suffix(file: Path):
        name = file.name
        idx = name.index('.jinja')
        return name[0:idx]

    @staticmethod
    def first_to_upper(string: str):
        """ Make sure the first letter is uppercase """
        return string[:1].upper() + string[1:]
