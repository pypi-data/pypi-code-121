import pathlib
from pathlib import Path
from typing import Optional, Tuple
import tempfile
import shutil
import joblib
import scipy.sparse
import random

from scipy.sparse import csr_matrix
import SumoNetVis
import tqdm
import matplotlib.pyplot as plt
from moviepy.editor import *

from sumo_output_parsers.tree_parser.fcd_parser import FcdMatrixObject, FCDFileParser
from sumo_output_parsers.logger_unit import logger


class TrafficAnimationVisualizer(object):
    def __init__(self,
                 path_sumo_net: pathlib.Path,
                 path_fcd_xml: Optional[pathlib.Path] = None,
                 tuple_fcd_matrix: Optional[Tuple[FcdMatrixObject, FcdMatrixObject]] = None,
                 path_working_dir: Optional[Path] = None,
                 skip_intervals: int = -1):
        """

        Args:
            path_sumo_net: path to net.xml file
            path_fcd_xml: path to fcd output file
            tuple_fcd_matrix: (fcd matrix of car x-positions, fcd matrix of car y-positions)
            path_working_dir: path to working directory
            skip_intervals: for approximation.
        """
        if path_fcd_xml is None and tuple_fcd_matrix is None:
            raise Exception('Either path_fcd_xml or fcd_matrix must be given.')
        # end if

        self.net = SumoNetVis.Net(path_sumo_net.__str__())
        self.path_sumo_net = path_sumo_net
        if tuple_fcd_matrix is None and path_fcd_xml is not None:
            x_position_matrix, y_position_matrix = self.generate_fcd_matrix(path_fcd_xml, skip_intervals)
        elif tuple_fcd_matrix is not None:
            __attrs = (tuple_fcd_matrix[0].value_type, tuple_fcd_matrix[1].value_type)
            assert __attrs == ('x', 'y'), \
                f'tuple_fcd_matrix must be (fcd-matrix-of-position-x, fcd-matrix-of-position-y).'
            x_position_matrix = tuple_fcd_matrix[0]
            y_position_matrix = tuple_fcd_matrix[1]
        else:
            raise NotImplementedError('undefined.')
        # end if
        self.x_position_matrix = x_position_matrix
        self.y_position_matrix = y_position_matrix

        if path_working_dir is None:
            self.path_working_dir = Path(tempfile.mkdtemp())
        else:
            self.path_working_dir = path_working_dir
        # end if

    @staticmethod
    def generate_fcd_matrix(path_fcd_output: Path, skip_intervals: int) -> Tuple[FcdMatrixObject, FcdMatrixObject]:
        logger.info('Parsing fcd output...')
        parser = FCDFileParser(path_fcd_output)
        x_position_matrix = parser.xml2matrix('x', skip_intervals=skip_intervals)
        y_position_matrix = parser.xml2matrix('y', skip_intervals=skip_intervals)
        logger.info('done fcd output')
        return x_position_matrix, y_position_matrix

    def generate_animation(self,
                           path_video_output: Path,
                           intervals: Optional[int] = -1,
                           is_keep_png_dir: bool = False,
                           n_samples: int = 100,
                           n_parallel: int = 4):
        """
        Args:
            path_video_output: A path to save the generated video.
            intervals: frames to render. if -1, it uses all frames. if None, it uses random sampling.
            is_keep_png_dir: If True, it does not delete png files.
            n_samples: the number of samples to use for the animation.
            n_parallel: A parameter of parallel jobs to generate png files.

        Returns:

        """
        assert path_video_output.parent.exists()

        length_time_intervals = self.x_position_matrix.matrix.shape[1]
        assert length_time_intervals == self.y_position_matrix.matrix.shape[1], \
            f'length of time-intervals does not match. length(x)={self.x_position_matrix.matrix.shape[1]} ' \
            f'length-y={self.y_position_matrix.matrix.shape[1]}'

        x_t = csr_matrix.transpose(self.x_position_matrix.matrix)
        y_t = csr_matrix.transpose(self.y_position_matrix.matrix)

        x_t_coo = scipy.sparse.coo_matrix(x_t)
        non_zero_rows = x_t_coo.nonzero()[0]
        # note: usually time-index==0 has an array with all 0 values.
        assert (len(set(non_zero_rows)) == len(self.x_position_matrix.interval_begins)) or \
               len(set(non_zero_rows)) + 1 == len(self.x_position_matrix.interval_begins)
        if len(set(non_zero_rows)) == len(self.x_position_matrix.interval_begins):
            seq_frame_samples = [(t, str(t_elem))
                                 for t, t_elem in zip(sorted(set(non_zero_rows)), self.x_position_matrix.interval_begins)]
        elif len(set(non_zero_rows)) + 1 == len(self.x_position_matrix.interval_begins):
            seq_frame_samples = [(0, self.x_position_matrix.interval_begins[0])]
            seq_frame_samples += [(t, str(t_elem))
                                  for t, t_elem
                                  in zip(sorted(set(non_zero_rows)), self.x_position_matrix.interval_begins[1:])]
        else:
            raise Exception()
        # end if

        if intervals is None:
            if len(seq_frame_samples) < n_samples:
                samples = seq_frame_samples
            else:
                samples = random.sample(seq_frame_samples, k=n_samples)
            # end if
        else:
            if len(seq_frame_samples) < intervals:
                samples = seq_frame_samples
            else:
                samples = [s for i, s in enumerate(seq_frame_samples) if i % intervals == 0]
            # end if
        # end if

        def __write_out_png(time_t, t_label, path_sumo_net, path_working_dir):
            sample_x = x_t[time_t].toarray()[0]
            sample_y = y_t[time_t].toarray()[0]
            fig, ax = plt.subplots()
            # self.net.plot(ax=ax)
            net = SumoNetVis.Net(path_sumo_net.__str__())
            net.plot(ax=ax)
            ax.scatter(sample_x, sample_y)
            ax.set_title(f"Time at {str(t_label)}")
            path_save_png = path_working_dir.joinpath(f'{time_t}.png')
            fig.savefig(path_save_png.__str__(), bbox_inches='tight')
            plt.close()
        # end def
        logger.info(f'Writing out png file with n-parallel={n_parallel}')
        joblib.Parallel(n_jobs=n_parallel)(
            joblib.delayed(__write_out_png)(
                t[0], t[1], self.path_sumo_net, self.path_working_dir) for t in samples)
        files = [str(p) for p in sorted(self.path_working_dir.glob('*.png'), key=lambda p: int(p.stem))]
        clip = ImageSequenceClip(files, fps=4)
        clip.write_videofile(path_video_output.__str__(), fps=24)
        logger.info(f'A video saved at {path_video_output}')

        if is_keep_png_dir:
            shutil.rmtree(self.path_working_dir)




