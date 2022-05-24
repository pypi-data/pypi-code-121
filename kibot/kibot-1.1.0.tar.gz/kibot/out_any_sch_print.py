# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
import os
from tempfile import mkdtemp
from shutil import rmtree, copy2
from .gs import GS
from .kiplot import check_eeschema_do, exec_with_retry, add_extra_options
from .misc import CMD_EESCHEMA_DO, kiauto_dependency
from .out_base import VariantOptions
from .kicad.config import KiConf
from .registrable import RegDependency
from .macros import macros, document, output_class  # noqa: F401
from . import log

logger = log.get_logger()


def register_deps(pre):
    RegDependency.register(kiauto_dependency(pre+'_sch_print'))


def copy_project(sch_dir):
    """ Copy the project file to the temporal dir """
    ext = GS.pro_ext
    source = GS.pro_file
    prj_file = os.path.join(sch_dir, GS.sch_basename+ext)
    if source is not None and os.path.isfile(source):
        copy2(source, prj_file)
        KiConf.fix_page_layout(prj_file)
    else:
        # Create a dummy project file to avoid warnings
        f = open(prj_file, 'wt')
        f.close()


class Any_SCH_PrintOptions(VariantOptions):
    def __init__(self):
        with document:
            self.monochrome = False
            """ Generate a monochromatic PDF """
            self.frame = True
            """ Include the frame and title block """
        super().__init__()
        self.add_to_doc('variant', "Not fitted components are crossed")
        self._expand_id = 'schematic'

    def get_targets(self, out_dir):
        if self.output:
            return [self._parent.expand_filename(out_dir, self.output)]
        return [self._parent.expand_filename(out_dir, '%f.%x')]

    def run(self, name):
        super().run(name)
        output_dir = os.path.dirname(name)
        check_eeschema_do()
        if self._comps:
            # Save it to a temporal dir
            sch_dir = mkdtemp(prefix='tmp-kibot-'+self._expand_ext+'_sch_print-')
            copy_project(sch_dir)
            fname = GS.sch.save_variant(sch_dir)
            sch_file = os.path.join(sch_dir, fname)
        else:
            sch_dir = None
            sch_file = GS.sch_file
        cmd = [CMD_EESCHEMA_DO, 'export', '--all_pages', '--file_format', self._expand_ext]
        if self.monochrome:
            cmd.append('--monochrome')
        if not self.frame:
            cmd.append('--no_frame')
        cmd.extend([sch_file, output_dir])
        cmd, video_remove = add_extra_options(cmd)
        ret = exec_with_retry(cmd)
        if ret:
            logger.error(CMD_EESCHEMA_DO+' returned %d', ret)
            exit(self._exit_error)
        if self.output:
            cur = self._parent.expand_filename(output_dir, '%f.%x')
            logger.debug('Moving '+cur+' -> '+name)
            os.rename(cur, name)
        # Remove the temporal dir if needed
        if sch_dir:
            logger.debug('Removing temporal variant dir `{}`'.format(sch_dir))
            rmtree(sch_dir)
        if video_remove:
            video_name = os.path.join(output_dir, 'export_eeschema_screencast.ogv')
            if os.path.isfile(video_name):
                os.remove(video_name)
