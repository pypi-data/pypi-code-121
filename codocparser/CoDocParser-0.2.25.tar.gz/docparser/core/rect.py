# -*- coding: utf-8 -*-
from docparser.config.excel.enums import VerticalAlignMode
from docparser.core.utils import Utils



class Rect:
    """
    区域信息
    """

    def __init__(self, sheet, rect_config):
        # 表单对象
        self.sheet = sheet
        # 区域配置
        self.rect_config = rect_config
        # 区域定位信息
        self.positions = dict()
        # 区域内数据行集合(存放表单原始Cell值)
        self.rows = []
        # 开始行-Sheet内
        self.start_row_in_sheet = 0
        # 开始行-Cell内
        self.start_row_in_cell = 0
        # 结束行-Cell内
        self.end_row_in_sheet = 0
        # 结束行-Cell内
        self.end_row_in_cell = 0
        # 开始列-Sheet内
        self.start_col_in_sheet = 0
        # 开始列-Cell内
        self.start_col_in_cell = 0
        # 结束列-Sheet内
        self.end_col_in_sheet = 0
        # 结束列-Cell内
        self.end_col_in_cell = 0

        self.__init_positions()
        self.__init_rect()
        self.__init_rows()

    def __init_positions(self):
        """
        初始化定位信息
        """
        matcheds = {}

        match_times = 0
        for r in range(1, self.sheet.max_row):
            for c in range(1, self.sheet.max_column):
                # 获取单元格值
                cell_value, max_row_in_cell, max_col_in_cell = str(Utils.get_sheet_cell_info(self.sheet, r, c))
                if cell_value is None or len(cell_value.strip()) == 0:
                    continue

                for p in ["left", "right", "top", "bottom"]:
                    # 获取定位的关键字
                    position_config = self.rect_config[p] if p in self.rect_config else None
                    if position_config is None:
                        continue

                    # 未配置关键字则不匹配
                    keyword = position_config["keyword"]
                    if len(keyword) == 0:
                        continue

                    # 根据关键字匹配在单元格内部位置
                    start_row_in_cell, start_col_in_cell = Utils.location_in_cell_pos(
                        cell_value, keyword)
                    if start_row_in_cell > -1:
                        # 确定第几次匹配
                        if match_times < position_config['match_times'] - 1:
                            match_times = match_times + 1
                            continue

                        if p == "left":
                            self.__init_left_position(position_config, r, c, keyword)
                        elif p == 'right':
                            self.__init_right_position(position_config, r, c, keyword)
                        elif p == 'top':
                            self.__init_top_position(position_config, r, c, keyword)
                        elif p == 'bottom':
                            self.__init_bottom_position(position_config, r, c, keyword)

                        matcheds[p + "_match"] = True

        # 验证区域存在关键是否匹配请阿卡
        errors = self.__valid_positions(matcheds)
        if len(errors.keys()) == 0:
            self.__adjust_missing_positions()

        return errors

    def __init_rect(self):
        """
        初始化区域信息
        """
        self.start_row_in_sheet = 0
        self.end_row_in_sheet = self.sheet.max_row
        self.start_col_in_sheet = 1
        self.end_col_in_sheet = self.sheet.max_column

        if "top" in self.positions:
            top_pos = self.positions["top"]
            self.start_row_in_sheet = top_pos["row_in_sheet"]
            self.start_row_in_cell = top_pos["row_in_cell"] + 1

        if "bottom" in self.positions:
            bottom_pos = self.positions["bottom"]
            self.end_row_in_sheet = bottom_pos["row_in_sheet"]
            self.end_row_in_cell = bottom_pos["row_in_cell"] - 1

        if "left" in self.positions:
            left_pos = self.positions["left"]
            self.start_col_in_sheet = left_pos["col_in_sheet"]
            self.start_col_in_cell = left_pos["col_in_cell"]

        if "right" in self.positions:
            right_pos = self.positions["right"]
            self.start_col_in_sheet = right_pos["col_in_sheet"]
            self.start_col_in_cell = right_pos["col_in_cell"]

    def __init_rows(self):
        """
        初始化数据行信息
        """
        for r in range(self.start_row_in_sheet, self.end_row_in_sheet):
            row = []
            for c in range(self.start_col_in_sheet, self.end_col_in_sheet):
                row.append(self.sheet.cell(r, c).value)
            self.rows.append(row)

    def __init_left_position(self, position_config, row, col, keyword):
        """
        初始化左侧定位信息
        """

        cell_value, row_count_in_cell, col_count_in_cell = Utils.get_sheet_cell_info(self.sheet, row, col)
        start_row_in_cell, start_col_in_cell = Utils.location_in_cell_pos(cell_value, keyword)

        temp_row_in_sheet = row
        temp_col_in_sheet = col
        temp_row_in_cell = start_row_in_cell
        temp_col_in_cell = start_col_in_cell

        # 如果关键不在区域内,则开始位置需要重新计算
        if position_config['is_outer']:
            temp_col_in_cell = temp_col_in_cell + len(keyword)

            # 如果关键字已经在末尾，则区域计算开始跳到下一个单元格
            if temp_col_in_cell >= col_count_in_cell:
                temp_col_in_sheet = temp_col_in_sheet + 1
                temp_col_in_cell = 0

        position_info = {
            "row_in_sheet": temp_row_in_sheet,
            "col_in_sheet": temp_col_in_sheet,
            "row_in_cell": temp_row_in_cell,
            "col_in_cell": temp_col_in_cell,
            "row_count_in_cell": row_count_in_cell,
            "col_count_in_cell": col_count_in_cell
        }

        self.positions['left'] = position_info

        # 根据左侧定位及对齐推测出TOP定位信息
        if 'top' not in self.positions and 'v_align' in position_config and position_config['v_align'] == VerticalAlignMode.top.name:
            self.positions['top'] = position_info

        # 根据左侧定位及对齐推测出Bottom定位信息
        if 'bottom' not in self.positions and 'v_align' in position_config and position_config['v_align'] == VerticalAlignMode.bottom.name:
            self.positions['bottom'] = position_info

        return position_info

    def __init_right_position(self, position_config, row, col, keyword):
        """
        初始化右侧定位信息
        """

        # 根据关键字匹配在单元格内部位置
        cell_value, row_count_in_cell, col_count_in_cell = Utils.get_sheet_cell_info(self.sheet, row, col)
        start_row_in_cell, start_col_in_cell = Utils.location_in_cell_pos(cell_value, keyword)

        temp_row_in_sheet = row
        temp_col_in_sheet = col
        temp_row_in_cell = start_row_in_cell
        temp_col_in_cell = start_col_in_cell

        # 如果关键不在区域内,则开始位置需要重新计算
        if not position_config['is_outer']:
            temp_col_in_cell = temp_col_in_cell + len(keyword)
        else:
            # 如果关键字已经在开始，则区域计算开始跳到上一个单元格
            if temp_col_in_cell == 0:
                temp_col_in_sheet = temp_col_in_sheet - 1
                _, _, max_col_in_cell = Utils.get_sheet_cell_info(self.sheet, row, col - 1)
                temp_col_in_cell = max_col_in_cell

        position_info = {
            "row_in_sheet": temp_row_in_sheet,
            "col_in_sheet": temp_col_in_sheet,
            "row_in_cell": temp_row_in_cell,
            "col_in_cell": temp_col_in_cell,
            "row_count_in_cell": row_count_in_cell,
            "col_count_in_cell": col_count_in_cell
        }

        self.positions['right'] = position_info

        # 根据右侧定位及对齐推测出TOP定位信息
        if 'top' not in self.positions and 'v_align' in position_config and position_config['v_align'] == VerticalAlignMode.top.name:
            self.positions['top'] = position_info

        # 根据右侧定位及对齐推测出Bottom定位信息
        if 'bottom' not in self.positions and 'v_align' in position_config and position_config['v_align'] == VerticalAlignMode.bottom.name:
            self.positions['bottom'] = position_info

        return position_info

    def __init_top_position(self, position_config, row, col, keyword):
        """
        初始化顶侧定位信息
        """

        # 根据关键字匹配在单元格内部位置
        cell_value, row_count_in_cell, col_count_in_cell = Utils.get_sheet_cell_info(self.sheet, row, col)
        start_row_in_cell, start_col_in_cell = Utils.location_in_cell_pos(cell_value, keyword)

        temp_row_in_sheet = row
        temp_col_in_sheet = col
        temp_row_in_cell = start_row_in_cell
        temp_col_in_cell = start_col_in_cell

        # 如果关键不在区域内,则开始位置需要重新计算
        if position_config['is_outer']:
            temp_row_in_cell = temp_row_in_cell + 1

            # 如果关键字已经在末尾，则区域计算开始跳到下一个单元格
            if temp_row_in_cell == row_count_in_cell:
                temp_row_in_sheet = temp_row_in_sheet + 1
                temp_row_in_cell = 0

        position_info = {
            "row_in_sheet": temp_row_in_sheet,
            "col_in_sheet": temp_col_in_sheet,
            "row_in_cell": temp_row_in_cell,
            "col_in_cell": temp_col_in_cell,
            "row_count_in_cell": row_count_in_cell,
            "col_count_in_cell": col_count_in_cell
        }

        self.positions['top'] = position_info

        # 根据右侧定位及对齐推测出TOP定位信息
        if 'left' not in self.positions and 'h_align' in position_config and position_config['h_align'] == VerticalAlignMode.left.name:
            self.positions['left'] = position_info

        # 根据右侧定位及对齐推测出Bottom定位信息
        if 'right' not in self.positions and 'h_align' in position_config and position_config['h_align'] == VerticalAlignMode.right.name:
            self.positions['right'] = position_info

        return position_info

    def __init_bottom_position(self, position_config, row, col, keyword):
        """
        初始化低侧定位信息
        """

        # 根据关键字匹配在单元格内部位置
        cell_value, row_count_in_cell, col_count_in_cell = Utils.get_sheet_cell_info(self.sheet, row, col)
        start_row_in_cell, start_col_in_cell = Utils.location_in_cell_pos(cell_value, keyword)

        temp_row_in_sheet = row
        temp_col_in_sheet = col
        temp_row_in_cell = start_row_in_cell
        temp_col_in_cell = start_col_in_cell

        # 如果关键不在区域内,则开始位置需要重新计算
        if position_config['is_outer']:
            if temp_row_in_cell == 0:
                temp_row_in_sheet = temp_row_in_sheet - 1
                _, max_row_in_cell, _ = Utils.get_sheet_cell_info(self.sheet, row - 1, col)
                temp_row_in_cell = max_row_in_cell

        position_info = {
            "row_in_sheet": temp_row_in_sheet,
            "col_in_sheet": temp_col_in_sheet,
            "row_in_cell": temp_row_in_cell,
            "col_in_cell": temp_col_in_cell,
            "row_count_in_cell": row_count_in_cell,
            "col_count_in_cell": col_count_in_cell
        }
        self.positions['bottom'] = position_info

        # 根据右侧定位及对齐推测出TOP定位信息
        if 'left' not in self.positions and 'h_align' in position_config and position_config['h_align'] == VerticalAlignMode.left.name:
            self.positions['left'] = position_info

        # 根据右侧定位及对齐推测出Bottom定位信息
        if 'right' not in self.positions and 'h_align' in position_config and position_config['h_align'] == VerticalAlignMode.right.name:
            self.positions['right'] = position_info

        return position_info

    def __valid_positions(self, matcheds):
        """
        验证定位信息是否配置正确
        """
        errors = dict()
        for p in ["left", "right", "top", "bottom"]:
            keyword = self.rect_config[p]['keyword'] if p in self.rect_config else ""
            if len(keyword) > 0 and (p + "_match" not in matcheds):
                errors[p + "_keyword"] = "【%s】未在文档中出现,请检查配置！" % keyword

        return errors
