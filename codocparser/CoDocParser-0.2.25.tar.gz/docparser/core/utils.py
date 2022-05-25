class Utils:

    @staticmethod
    def location_in_cell_pos(cell_value, keyword):
        """
        查找内容所在单元各格内行号,列号,文本总行数，文本列内容最大长度
        """
        start_row_in_cell = -1
        start_col_in_cell = -1
        if len(keyword) > 0 and keyword in cell_value:
            lines = cell_value.strip().split("\n")
            for row, line in enumerate(lines):
                col = line.find(keyword)
                if col > -1:
                    start_row_in_cell = row
                    start_col_in_cell = col
                    break

        return start_row_in_cell, start_col_in_cell

    @staticmethod
    def get_text_block_value(cell_value, row, start_col, length):
        """
        查找内容所在行号,列号
        """
        lines = cell_value.strip().split("\n")

        return lines[row][start_col, length]

    @staticmethod
    def get_sheet_cell_value(sheet, row, col):
        """
        获取Excel表单单元格值
        :param sheet: 行
        :param row: 行
        :param col: 列
        :return: 返回值
        """
        if row > sheet.max_row or col > sheet.max_column:
            return None

        cell_value = sheet.cell(row, col).value

        return "" if cell_value is None else cell_value

    @staticmethod
    def get_sheet_cell_info(sheet, row, col):
        """
        获取Excel表单单元格值
        :param sheet: 行
        :param row: 行
        :param col: 列
        :return: 返回值
        """
        if row > sheet.max_row or col > sheet.max_column:
            return None

        cell_value = sheet.cell(row, col).value

        cell_value = "" if cell_value is None else cell_value

        lines = cell_value.strip().split("\n")
        row_count_in_cell = len(lines)
        col_count_in_cell = 0
        for row, line in enumerate(lines):
            if len(line) > col_count_in_cell:
                col_count_in_cell = len(line)

        return cell_value, row_count_in_cell, col_count_in_cell

    @staticmethod
    def process_rect_config(sheet, rect_config):
        """
        预检查区域配置数据
        :param sheet: 区域配置
        :param rect_config: 区域配置
        :return: 返回配置错误信息
        """
        errors = {}
        matchs = {}
        rect = rect_config

        for r in range(1, sheet.max_row):
            for c in range(1, sheet.max_column):
                cell_value = str(ExcelExtractorUtils.get_sheet_cell_value(sheet, r, c))
                if cell_value is None or len(cell_value.strip()) == 0:
                    continue

                for p in ["left", "right", "top", "bottom"]:
                    keyword = rect[p + "_keyword"] if p + "_keyword" in rect else ""
                    text_row, text_col, text_row_count, text_col_count = ExcelExtractorUtils.location_text_in_cell_pos(
                        cell_value, keyword)
                    matchs[p + "_match"] = False

                    if text_row > -1 and p + "_pos" not in rect:
                        if p == "left":
                            text_col = text_col + len(keyword)
                        rect[p + "_pos"] = {
                            "sheet_row": r,
                            "sheet_col": c,
                            "text_row": text_row,
                            "text_col": text_col,
                            "text_row_count": text_row_count,
                            "text_col_count": text_col_count
                        }
                        matchs[p + "_match"] = True

        # 验证区域关键
        for p in ["left", "right", "top", "bottom"]:
            keyword = rect[p + "_keyword"] if p + "_keyword" in rect else ""
            if len(keyword) > 0 and (p + "_match" not in matchs):
                errors[p + "_keyword"] = "【%s】未在文档中出现,请检查配置！" % keyword

        return errors

    @staticmethod
    def normalization_rect_data(sheet, normalization_rect):
        """
        规范化文本块区域以便准确提取文本
         :param sheet: 区域配置
         :param normalization_rect: 区域配置
        """
        row_datas = dict()
        for r in range(normalization_rect["start_row"], normalization_rect["end_row"] + 1):
            cell_datas = dict()
            max_text_lines = 0
            start_text_lines = 0
            end_text_lines = 0

            if r == normalization_rect["start_row"]:
                start_text_lines = normalization_rect["text_start_row"]

            if r == normalization_rect["end_row"]:
                end_text_lines = normalization_rect["text_end_row"]

            for c in range(normalization_rect["start_col"], normalization_rect["end_col"] + 1):
                cell_value = str(ExcelExtractorUtils.get_sheet_cell_value(sheet, r, c))
                lines = cell_value.split("\n")

                if len(lines) > max_text_lines:
                    max_text_lines = len(lines)

                t_lines = []
                if normalization_rect["start_col"] == normalization_rect["end_col"]:
                    for l in lines:
                        t_lines.append(l[normalization_rect["text_start_col"]:normalization_rect["text_end_col"]])
                else:
                    if normalization_rect["start_col"] == c:
                        for l in lines:
                            t_lines.append(l[normalization_rect["text_start_col"]:len(l)])
                    elif normalization_rect["end_col"] == c:
                        for l in lines:
                            t_lines.append(l[0:normalization_rect["text_end_col"]])
                    else:
                        t_lines = lines

                cell_datas[c] = t_lines

            if end_text_lines == -1:
                end_text_lines = max_text_lines - 1
            row_datas[r] = {
                "max_text_lines": max_text_lines,
                "start_text_lines": start_text_lines,
                "end_text_lines": end_text_lines,
                "cells": cell_datas
            }

        normalization_rect_data = [
            [0 for col in range(normalization_rect["end_col"] - normalization_rect["start_col"] + 1)] for row in
            range(normalization_rect["end_row"] - normalization_rect["start_row"] + 1)]
        for row in row_datas.keys():
            max_text_lines = row_datas[row]["max_text_lines"]
            cells = row_datas[row]["cells"]
            for c in cells.keys():
                cell_value = cells[c]
                normalization_cell_value = ExcelExtractorUtils.__normalization_array(cell_value, max_text_lines)
                normalization_rect_data[row - normalization_rect["start_row"]][
                    c - normalization_rect["start_col"]] = normalization_cell_value

        return normalization_rect_data, row_datas

    @staticmethod
    def __normalization_array(arr, line_count):
        length = len(arr)
        if length < line_count:
            for i in range(0, line_count - length):
                arr.append("")

        return arr

    @staticmethod
    def normalization_rect(sheet, rect):
        """
        规范化文本块区域以便准确提取文本
         :param sheet: 区域配置
         :param rect: 区域配置
        """
        start_row = 0
        end_row = sheet.max_row
        start_col = 1
        end_col = sheet.max_column

        text_start_row = 0
        text_end_row = 0
        text_start_col = 0
        text_end_col = 0
        if "top_pos" in rect:
            top_pos = rect["top_pos"]
            start_row = top_pos["sheet_row"]
            text_start_row = top_pos["text_row"] + 1
            if top_pos["text_row"] == top_pos["text_row_count"] - 1:
                start_row = start_row + 1
                text_start_row = 0
        else:
            if "left_pos" in rect:
                left_pos = rect["left_pos"]
                start_row = left_pos["sheet_row"]
                text_start_row = left_pos["text_row"]
            elif "right_pos" in rect:
                right_pos = rect["right_pos"]
                start_row = right_pos["sheet_row"]
                text_start_row = right_pos["text_row"]

        if "bottom_pos" in rect:
            bottom_pos = rect["bottom_pos"]
            end_row = bottom_pos["sheet_row"]
            text_end_row = bottom_pos["text_row"] - 1

            if bottom_pos["text_row"] == 0:
                end_row = end_row - 1
                text_end_row = -1
        else:
            if "left_pos" in rect:
                left_pos = rect["left_pos"]
                end_row = left_pos["sheet_row"]
                text_end_row = left_pos["text_row"]
            elif "right_pos" in rect:
                right_pos = rect["right_pos"]
                end_row = right_pos["sheet_row"]
                text_end_row = right_pos["text_row"]

        if "left_pos" in rect:
            left_pos = rect["left_pos"]
            start_col = left_pos["sheet_col"]
            text_start_col = left_pos["text_col"]

        if "right_pos" in rect:
            right_pos = rect["right_pos"]
            end_col = right_pos["sheet_col"]
            text_end_col = right_pos["text_col"]

        return {"start_row": start_row, "end_row": end_row, "start_col": start_col, "end_col": end_col,
                "text_start_row": text_start_row, "text_end_row": text_end_row, "text_start_col": text_start_col,
                "text_end_col": text_end_col}
