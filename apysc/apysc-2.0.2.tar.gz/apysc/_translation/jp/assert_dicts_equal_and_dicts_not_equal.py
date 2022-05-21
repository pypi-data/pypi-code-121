"""This module is for the translation mapping data of the
following document:

Document file: assert_dicts_equal_and_dicts_not_equal.md
Language: jp
"""

from typing import Dict

MAPPING: Dict[str, str] = {

    '# assert_dicts_equal and assert_dicts_not_equal interfaces':
    '# assert_dicts_equal と assert_dicts_not_equal インターフェイス',

    'This page explains the `assert_dicts_equal` and `assert_dicts_not_equal` function interfaces.':  # noqa
    'このページでは`assert_dicts_equal`と`assert_dicts_not_equal`の各関数のインターフェイスについて説明します。',  # noqa

    '## What interfaces are these?':
    '## 各インターフェイスの概要',

    'The `assert_dicts_equal` function interface asserts specified two dictionaries (`dict` or `Dictionary` type value) are equal. Conversely, the `assert_dicts_not_equal` function interface asserts specified two dictionaries are not equal.':  # noqa
    '`assert_dicts_equal`関数のインターフェイスは指定された2つの辞書（`Dictionary`型など）の値が一致しているかをチェックします。逆に`assert_dicts_not_equal`関数のインターフェイスは指定された2つの辞書の値が一致していないことをチェックします。',  # noqa

    '## See also':
    '## 関連資料',

    '- [JavaScript assertion interface basic behavior](assertion_basic_behavior.md)':  # noqa
    '- [JavaScriptの各アサーションのインターフェイスの基本的な挙動](jp_assertion_basic_behavior.md)',  # noqa

    '## Basic usage':
    '## 基本的な使い方',

    'Both of the `assert_dicts_equal` and `assert_dicts_not_equal` interfaces require the `left` and `right` arguments. The `msg` argument is optional.':  # noqa
    '`assert_dicts_equal`と`assert_dicts_not_equal`の各インターフェイスは`left`と`right`引数を必要とします。`msg`引数は省略可です。',  # noqa

    'You can specify a Python built-in `dict` and `Dictionary` values to these arguments.':  # noqa
    '各インターフェイスにはPythonビルトインの`dict`やapyscの`Dictionary`の値を引数として指定することができます。',

    'The following example (`assert_dicts_equal` and values are equal) passes:':  # noqa
    '以下の例では`assert_dicts_equal`関数を使って値が同じ辞書に対してチェックを行っています（チェックは通ります）。',

    '```py\n# runnable\nimport apysc as ap\n\nstage: ap.Stage = ap.Stage(\n    stage_width=0, stage_height=0, background_color=\'#333\',\n    stage_elem_id=\'stage\')\n\ndict_val: ap.Dictionary = ap.Dictionary({\'a\': 10, \'b\': 20})\nap.assert_dicts_equal(\n    left={\'a\': 10, \'b\': 20}, right=dict_val,\n    msg=\'Values are not equal!\')\n\nap.save_overall_html(\n    dest_dir_path=\'assert_dicts_equal_basic_usage_1/\')\n```':  # noqa
    '```py\n# runnable\nimport apysc as ap\n\nstage: ap.Stage = ap.Stage(\n    stage_width=0, stage_height=0, background_color=\'#333\',\n    stage_elem_id=\'stage\')\n\ndict_val: ap.Dictionary = ap.Dictionary({\'a\': 10, \'b\': 20})\nap.assert_dicts_equal(\n    left={\'a\': 10, \'b\': 20}, right=dict_val,\n    msg=\'Values are not equal!\')\n\nap.save_overall_html(\n    dest_dir_path=\'assert_dicts_equal_basic_usage_1/\')\n```',  # noqa

    '```\n[assert_dicts_equal]\nLeft value: {a: 10, b: 20} right value: dct_1\n```':  # noqa
    '```\n[assert_dicts_equal]\nLeft value: {a: 10, b: 20} right value: dct_1\n```',  # noqa

    'The following example (`assert_dicts_equal` and values are not equal)  fails:':  # noqa
    '以下の例では`assert_dicts_equal`関数を使って値が一致していない辞書に対してチェックを行っています（チェックは失敗します）。',  # noqa

    '```py\n# runnable\nimport apysc as ap\n\nstage: ap.Stage = ap.Stage(\n    stage_width=0, stage_height=0, background_color=\'#333\',\n    stage_elem_id=\'stage\')\n\ndict_val: ap.Dictionary = ap.Dictionary({\'a\': 10, \'b\': 20})\nap.assert_dicts_equal(\n    left={\'a\': 30}, right=dict_val, msg=\'Values are not equal!\')\n\nap.save_overall_html(\n    dest_dir_path=\'assert_dicts_equal_basic_usage_2/\')\n```':  # noqa
    '```py\n# runnable\nimport apysc as ap\n\nstage: ap.Stage = ap.Stage(\n    stage_width=0, stage_height=0, background_color=\'#333\',\n    stage_elem_id=\'stage\')\n\ndict_val: ap.Dictionary = ap.Dictionary({\'a\': 10, \'b\': 20})\nap.assert_dicts_equal(\n    left={\'a\': 30}, right=dict_val, msg=\'Values are not equal!\')\n\nap.save_overall_html(\n    dest_dir_path=\'assert_dicts_equal_basic_usage_2/\')\n```',  # noqa

    '```\n[assert_dicts_equal]\nLeft value: {a: 30} right value: dct_1\n...\nAssertion failed: Values are not equal!\n```':  # noqa
    '```\n[assert_dicts_equal]\nLeft value: {a: 30} right value: dct_1\n...\nAssertion failed: Values are not equal!\n```',  # noqa

    'The following example (`assert_dicts_not_equal` and values are not equal) passes:':  # noqa
    '以下の例では`assert_dicts_not_equal`関数を使って値が一致していない辞書に対してチェックを行っています（チェックは通ります）。',  # noqa

    '```py\n# runnable\nimport apysc as ap\n\nstage: ap.Stage = ap.Stage(\n    stage_width=0, stage_height=0, background_color=\'#333\',\n    stage_elem_id=\'stage\')\n\ndict_val: ap.Dictionary = ap.Dictionary({\'a\': 10, \'b\': 20})\nap.assert_dicts_not_equal(\n    left={\'a\': 30}, right=dict_val, msg=\'Values are equal!\')\n\nap.save_overall_html(\n    dest_dir_path=\'assert_dicts_not_equal_basic_usage_1/\')\n```':  # noqa
    '```py\n# runnable\nimport apysc as ap\n\nstage: ap.Stage = ap.Stage(\n    stage_width=0, stage_height=0, background_color=\'#333\',\n    stage_elem_id=\'stage\')\n\ndict_val: ap.Dictionary = ap.Dictionary({\'a\': 10, \'b\': 20})\nap.assert_dicts_not_equal(\n    left={\'a\': 30}, right=dict_val, msg=\'Values are equal!\')\n\nap.save_overall_html(\n    dest_dir_path=\'assert_dicts_not_equal_basic_usage_1/\')\n```',  # noqa

    '```\n[assert_dicts_not_equal]\nLeft value: {a: 30} right value: dct_1\n```':  # noqa
    '```\n[assert_dicts_not_equal]\nLeft value: {a: 30} right value: dct_1\n```',  # noqa

    '## Notes for the assert_equal and assert_not_equal interfaces':
    '## assert_equal と assert_not_equal の各インターフェイスにおける特記事項',

    'If a `Dictionary` value is specified to the `assert_equal` or `assert_not_equal` interface\'s argument value, then the `assert_dicts_equal` or `assert_dicts_not_equal` interfaces will be called instead of the `assert_equal` or `assert_not_equal` interfaces automatically.':  # noqa
    'もし`assert_equal`もしくは`assert_not_equal`のインターフェイスの引数へ`Dictionary`の値が指定された場合、自動的に`assert_dicts_equal`もしくは`assert_dicts_not_equal`のインターフェイスがそれらのインターフェイスの代わりに呼ばれます。',  # noqa

    '```py\n# runnable\nimport apysc as ap\n\nstage: ap.Stage = ap.Stage(\n    stage_width=0, stage_height=0, background_color=\'#333\',\n    stage_elem_id=\'stage\')\n\ndict_val: ap.Dictionary = ap.Dictionary({\'a\': 30})\nap.assert_equal(\n    left={\'a\': 30}, right=dict_val,\n    msg=\'Values are not equal!\')\n\nap.save_overall_html(\n    dest_dir_path=\'assert_dicts_equal_notes_for_assert_equal/\')\n```':  # noqa
    '```py\n# runnable\nimport apysc as ap\n\nstage: ap.Stage = ap.Stage(\n    stage_width=0, stage_height=0, background_color=\'#333\',\n    stage_elem_id=\'stage\')\n\ndict_val: ap.Dictionary = ap.Dictionary({\'a\': 30})\nap.assert_equal(\n    left={\'a\': 30}, right=dict_val,\n    msg=\'Values are not equal!\')\n\nap.save_overall_html(\n    dest_dir_path=\'assert_dicts_equal_notes_for_assert_equal/\')\n```',  # noqa

    '```\n[assert_dicts_equal]\nLeft value: {a: 30} right value: dct_1\n```':  # noqa
    '```\n[assert_dicts_equal]\nLeft value: {a: 30} right value: dct_1\n```',  # noqa

    '## assert_dicts_equal API':
    '## assert_dicts_equal API',

    '<span class="inconspicuous-txt">Note: the document build script generates and updates this API document section automatically. Maybe this section is duplicated compared with previous sections.</span>':  # noqa
    '<span class="inconspicuous-txt">特記事項: このAPIドキュメントはドキュメントビルド用のスクリプトによって自動で生成・同期されています。そのためもしかしたらこの節の内容は前節までの内容と重複している場合があります。</span>',  # noqa

    '**[Interface summary]** JavaScript assertion interface for Dictionary values equal condition.<hr>':  # noqa
    '**[インターフェイス概要]** JavaScript上での辞書の等値条件のチェックを行うインターフェイスです。<hr>',

    '**[Parameters]**':
    '**[引数]**',

    '- `left`: *':
    '- `left`: *',

    '  - Left-side value to compare.':
    '  - 比較用の左辺の値。',

    '- `right`: *':
    '- `right`: *',

    '  - Right-side value to compare.':
    '  - 比較用の右辺の値。',

    '- `msg`: str, optional':
    '- `msg`: str, optional',

    '  - Message to display when assertion failed.':
    '  - チェックに失敗した際に表示するメッセージ。',

    '<hr>':
    '<hr>',

    '**[Notes]**':
    '**[特記事項]**',

    'This interface is used instead of assert_equal for Dictionary class comparison (JavaScript can not compare dictionary (Object) directly, like a Python, for example, `{"a": 10} === {"a": 10}` becomes false).<hr>':  # noqa
    'このインターフェイスは`assert_equal`関数での`Dictionary`のクラスの値の比較時には代わりに使用されます（JavaScriptではPythonと異なり辞書の値を直接比較できないため）。<hr>',  # noqa

    '**[Examples]**':
    '**[コードサンプル]**',

    '```py\n>>> import apysc as ap\n>>> dict_1: ap.Dictionary = ap.Dictionary({\'a\': 10})\n>>> dict_2: ap.Dictionary = ap.Dictionary({\'a\': 10})\n>>> ap.assert_dicts_equal(dict_1, dict_2)\n```':  # noqa
    '```py\n>>> import apysc as ap\n>>> dict_1: ap.Dictionary = ap.Dictionary({\'a\': 10})\n>>> dict_2: ap.Dictionary = ap.Dictionary({\'a\': 10})\n>>> ap.assert_dicts_equal(dict_1, dict_2)\n```',  # noqa

    '## assert_dicts_not_equal API':
    '## assert_dicts_not_equal API',

    '<span class="inconspicuous-txt">Note: the document build script generates and updates this API document section automatically. Maybe this section is duplicated compared with previous sections.</span>':  # noqa
    '<span class="inconspicuous-txt">特記事項: このAPIドキュメントはドキュメントビルド用のスクリプトによって自動で生成・同期されています。そのためもしかしたらこの節の内容は前節までの内容と重複している場合があります。</span>',  # noqa

    '**[Interface summary]** JavaScript assertion interface for Dictionary values not equal condition.<hr>':  # noqa
    '**[インターフェイス概要]** JavaScript上での辞書の非等値のチェックを行うインターフェイスです。<hr>',

    '**[Parameters]**':
    '**[引数]**',

    '- `left`: *':
    '- `left`: *',

    '  - Left-side value to compare.':
    '  - 比較用の左辺の値。',

    '- `right`: *':
    '- `right`: *',

    '  - Right-side value to compare.':
    '  - 比較用の右辺の値。',

    '- `msg`: str, optional':
    '- `msg`: str, optional',

    '  - Message to display when assertion failed.':
    '  - チェックに失敗した際に表示するメッセージ。',

    '<hr>':
    '<hr>',

    '**[Notes]**':
    '**[特記事項]**',

    'This interface is used instead of assert_not_equal for Dictionary class comparison (JavaScript can not compare dictionary (Object) directly, like a Python, for example, `{"a": 10} !== {"a": 10}` becomes true).<hr>':  # noqa
    'このインターフェイスは`assert_not_equal`関数での`Dictionary`クラスの値の比較時には代わりに使用されます（JavaScriptではPythonと異なり辞書の値を直接比較できないため）。<hr>',  # noqa

    '**[Examples]**':
    '**[コードサンプル]**',

    '```py\n>>> import apysc as ap\n>>> dict_1: ap.Dictionary = ap.Dictionary({\'a\': 10})\n>>> dict_2: ap.Dictionary = ap.Dictionary({\'a\': 20})\n>>> ap.assert_dicts_not_equal(dict_1, dict_2)\n```':  # noqa
    '```py\n>>> import apysc as ap\n>>> dict_1: ap.Dictionary = ap.Dictionary({\'a\': 10})\n>>> dict_2: ap.Dictionary = ap.Dictionary({\'a\': 20})\n>>> ap.assert_dicts_not_equal(dict_1, dict_2)\n```',  # noqa

}
