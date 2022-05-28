import os

from typing import TYPE_CHECKING
from typing import List

from cleo.terminal import Terminal
from coverage import Coverage as _Coverage


if TYPE_CHECKING:
    from cleo.io.io import IO


class Coverage(_Coverage):
    def __init__(self, io: "IO", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._io = io
        self._warnings = []

    @property
    def warnings(self) -> List[str]:
        return self._warnings

    def _warn(self, msg, slug=None, once=False):
        if self._no_warn_slugs is None:
            self._no_warn_slugs = list(self.config.disable_warnings)

        if slug in self._no_warn_slugs:
            # Don't issue the warning
            return

        self._warnings.append(msg)

        if once:
            self._no_warn_slugs.append(slug)


class CoverageReporter:
    def __init__(self, io: "IO") -> None:
        self._io = io
        self._terminal = Terminal()

    def render(self, coverage: "Coverage") -> None:
        data = coverage.get_data()

        max_width = min(self._terminal.width, 88)
        max_filename_length = 0
        analysis = []
        total_stmts = 0
        total_missed_stmts = 0
        for file_name in sorted(data.measured_files()):
            file_name, stmts, excluded_stmts, missed_stmts, lines = coverage.analysis2(
                file_name
            )
            file_name = os.path.relpath(file_name, os.getcwd())
            max_filename_length = max(max_filename_length, len(file_name))
            analysis.append(
                (
                    file_name,
                    lines,
                    (1 - len(missed_stmts) / len(stmts)) * 100 if stmts else 100,
                )
            )
            total_stmts += len(stmts)
            total_missed_stmts += len(missed_stmts)

        total = (1 - total_missed_stmts / total_stmts) * 100 if total_stmts else 100
        total_color = "yellow"
        if total == 100:
            total_color = "green"
        elif total == 0:
            total_color = "red"

        self._io.write_line(
            f"  <fg=default;options=bold>Cov:    </><fg={total_color};options=bold>{total:0.1f}%</>"
        )
        self._io.write_line("")

        if coverage.warnings:
            for warning in coverage.warnings:
                self._io.write_error_line(f"  <fg=yellow>{warning}</>")

            self._io.write_line("")

        left_padding = 2
        right_padding = 2
        coverage_value_width = 7
        file_name_right_padding = 1
        coverage_value_left_padding = 1
        extraneous_width = (
            left_padding
            + file_name_right_padding
            + coverage_value_left_padding
            + coverage_value_width
            + right_padding
        )
        missed_lines_left_padding = 2
        missed_lines_right_padding = (
            coverage_value_left_padding + coverage_value_width + right_padding
        )

        for analysis_section in analysis:
            file_name, missed_lines, coverage = analysis_section
            needed_width = len(file_name) + extraneous_width
            file_name_parts = file_name.split(os.sep)
            formatted_file_name = "<fg=default;options=bold>{}</>".format(
                f"<fg=default;options=dark>{os.sep}</>".join(file_name_parts)
            )
            line = f"  {formatted_file_name}"

            color = "yellow"
            if coverage == 100:
                color = "green"
            elif coverage == 0:
                color = "red"

            coverage = f"{coverage:0.1f}"

            if not missed_lines:
                # Adding dot padding
                dot_padding = max_width - needed_width
                line += "{}{}".format(
                    " " * file_name_right_padding,
                    "<fg=default;options=dark>.</>" * dot_padding,
                )

                line += "{}<fg={}>{}{}</> %{}".format(
                    " " * coverage_value_left_padding,
                    color,
                    "".rjust(5 - len(str(coverage)), " "),
                    coverage,
                    " " * right_padding,
                )
            else:
                missed_lines_parts = missed_lines.split(", ")
                current_width = len(file_name) + len(missed_lines) + extraneous_width

                # If everything fits in one line write it
                if current_width <= max_width:
                    line += "{}{}".format(
                        " " * file_name_right_padding,
                        "<fg=default;options=dark>, </>".join(
                            f"<fg=red>{ml}</>" for ml in missed_lines.split(", ")
                        ),
                    )
                    dot_padding = max_width - current_width

                    line += "{}{}".format(
                        " " * file_name_right_padding,
                        "<fg=default;options=dark>.</>" * (dot_padding - 1),
                    )

                    line += "{}<fg={}>{}{}</> %{}".format(
                        " " * coverage_value_left_padding,
                        color,
                        "".rjust(5 - len(str(coverage)), " "),
                        coverage,
                        " " * right_padding,
                    )
                else:
                    # Adding dot padding
                    dot_padding = max_width - needed_width
                    line += "{}{}".format(
                        " " * file_name_right_padding,
                        "<fg=default;options=dark>.</>" * dot_padding,
                    )

                    line += "{}<fg={}>{}{}</> %{}".format(
                        " " * coverage_value_left_padding,
                        color,
                        "".rjust(5 - len(str(coverage)), " "),
                        coverage,
                        " " * right_padding,
                    )

                    self._io.write_line(line)

                    missed_lines_part = missed_lines_parts.pop(0)
                    current_width = (
                        len(missed_lines_part)
                        + (2 if missed_lines_parts else 0)
                        + missed_lines_left_padding
                        + left_padding
                    )

                    # Starting a new line with missed lines
                    line = "{}<fg=red>{}</>{}".format(
                        " " * (left_padding + missed_lines_left_padding),
                        missed_lines_part,
                        "<fg=default;options=dark>,</> " if missed_lines_parts else "",
                    )
                    while missed_lines_parts:
                        missed_lines_part = missed_lines_parts.pop(0)
                        current_width += len(missed_lines_part) + (
                            2 if missed_lines_parts else 0
                        )

                        if current_width > max_width - missed_lines_right_padding:
                            self._io.write_line(line)
                            line = "{}<fg=red>{}</>{}".format(
                                " " * (left_padding + missed_lines_left_padding),
                                missed_lines_part,
                                "<fg=default;options=dark>,</> "
                                if missed_lines_parts
                                else "",
                            )
                            current_width = (
                                len(missed_lines_part)
                                + (2 if missed_lines_parts else 0)
                                + missed_lines_left_padding
                                + left_padding
                            )
                        else:
                            line += f"<fg=red>{missed_lines_part}</>"

                            if missed_lines_parts:
                                line += "<fg=default;options=dark>,</> "

            self._io.write_line(line)
