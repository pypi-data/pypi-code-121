import re

from tdf_tools.tools.print import Print


class RegularTool:

    __replace_sign = r"#@^&#%&%*$#"

    # 删除埋点
    def delete_track(content: str) -> str:
        m = re.compile(r"TDFAnalytics.track.track\([^\(]*?\);")
        outtmp = re.sub(m, "", content)
        return outtmp

    # 删除备注
    def delete_remark(content: str) -> str:
        m = re.compile(r"//.*")
        outtmp = re.sub(m, "", content)
        return outtmp

    # 删除弃用
    def delete_deprecated(content: str) -> str:
        m = re.compile(r"@Deprecated\(.*?\)")
        outtmp = re.sub(m, "", content)
        return outtmp

    # 删除 @router 相关的文案
    def delete_router(content: str) -> str:
        m = re.compile(r"@TZRouter\([^\(]*?\)")
        outtmp = re.sub(m, "", content)
        return outtmp

    # 寻找带 .intl 后缀的文本，匹配出来是不带 "" 或者 '' 的字符
    def find_intl_str(content: str) -> list[str]:
        matchs_d = RegularTool.__match_str(
            content,
            r"\"",
            r"(?<=\")[^\"\f\n\r\t\v]*?[\u4E00-\u9FA5][^\"\f\n\r\t\v]*?(?=\"\s*\.intl)",
        )
        matchs_s = RegularTool.__match_str(
            content,
            r"\'",
            r"(?<=\')[^\"\f\n\r\t\v]*?[\u4E00-\u9FA5][^\"\f\n\r\t\v]*?(?=\'\s*\.intl)",
        )
        return matchs_d + matchs_s

    # 删除带 .intl 后缀的文本
    def delete_intl_str(content: str) -> str:
        outtmp = RegularTool.__delete_str(
            content,
            r"\"",
            r'"[^\"\f\n\r\t\v]*?[\u4E00-\u9FA5][^\"\f\n\r\t\v]*?"\s*\.intl',
        )
        outtmp = RegularTool.__delete_str(
            outtmp,
            r"\'",
            r"'[^\"\f\n\r\t\v]*?[\u4E00-\u9FA5][^\"\f\n\r\t\v]*?'\s*\.intl",
        )
        return outtmp

    # 寻找没国际化的中文字符串，匹配出来是不带 "" 或者 '' 的字符
    def find_chinese_str(content: str) -> list[str]:
        matchs_d = RegularTool.__match_str(
            content,
            r"\"",
            r'"[^\"\f\n\r\t\v]*?[\u4E00-\u9FA5][^\"\f\n\r\t\v]*?"(?!\.intl)',
        )
        matchs_d = list(map(lambda x: x.strip(r'"'), matchs_d))
        matchs_s = RegularTool.__match_str(
            content,
            r"\'",
            r"'[^\'\f\n\r\t\v]*?[\u4E00-\u9FA5][^\'\f\n\r\t\v]*?'(?!\.intl)",
        )
        matchs_s = list(map(lambda x: x.strip(r"'"), matchs_s))
        return matchs_d + matchs_s

    # 没国际化的中文字符串 追加 .intl
    def replace_chinese_str(content: str, old_str: str) -> str:

        q_sign = r"\""
        content = content.replace(q_sign, RegularTool.__replace_sign)
        m = re.compile(r'"[^\"\f\n\r\t\v]*?[\u4E00-\u9FA5][^\"\f\n\r\t\v]*?"(?!\.intl)')
        content: str = re.sub(m, RegularTool.__append_Suffix, content)
        content = content.replace(RegularTool.__replace_sign, q_sign)

        s_sign = r"\'"
        content = content.replace(s_sign, RegularTool.__replace_sign)
        m = re.compile(r"'[^\'\f\n\r\t\v]*?[\u4E00-\u9FA5][^\'\f\n\r\t\v]*?'(?!\.intl)")
        content = re.sub(m, RegularTool.__append_Suffix, content)
        content = content.replace(RegularTool.__replace_sign, s_sign)

        return content

    def __append_Suffix(matched):
        # 找到字母，把原字母 添加 .intl
        tempstr = matched.group()  # 取查找到的字符/串
        tempstr = tempstr + ".intl"  # 格式化
        return tempstr

    # 删除匹配的字符串
    def __delete_str(content: str, sign: str, pattern: str) -> str:
        content = content.replace(sign, RegularTool.__replace_sign)
        m = re.compile(pattern)
        outtmp = re.sub(m, "", content)
        return outtmp

    # 匹配 字符串，无法处理的符号先替换，然后再处理
    def __match_str(content: str, sign: str, pattern: str) -> list[str]:
        match_strs = []
        content = content.replace(sign, RegularTool.__replace_sign)
        matchs: list[str] = re.findall(pattern, content)
        for m in matchs:
            new_str = m.replace(RegularTool.__replace_sign, sign)
            match_strs.append(new_str)
        return match_strs

    # 寻找 intl 的 import 字符
    def find_intl_imports(content: str) -> list[str]:
        pattern = r"import '.*_i18n.dart';"
        matchs = re.findall(pattern, content)
        return matchs

    # 替换 intl 的 import
    def replace_intl_imports(content: str, replace_str: str) -> str:
        m = re.compile(r"import '.*_i18n.dart';")
        outtmp = re.sub(m, replace_str, content)
        return outtmp
