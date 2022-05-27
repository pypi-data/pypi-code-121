from setuptools import setup

name = "types-openpyxl"
description = "Typing stubs for openpyxl"
long_description = '''
## Typing stubs for openpyxl

This is a PEP 561 type stub package for the `openpyxl` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `openpyxl`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/openpyxl. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `2d2b34c1ee25f9c63554250d2b5f897a395ae300`.
'''.lstrip()

setup(name=name,
      version="3.0.3",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/openpyxl.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['openpyxl-stubs'],
      package_data={'openpyxl-stubs': ['__init__.pyi', '_constants.pyi', 'cell/__init__.pyi', 'cell/_writer.pyi', 'cell/cell.pyi', 'cell/read_only.pyi', 'cell/text.pyi', 'chart/_3d.pyi', 'chart/__init__.pyi', 'chart/_chart.pyi', 'chart/area_chart.pyi', 'chart/axis.pyi', 'chart/bar_chart.pyi', 'chart/bubble_chart.pyi', 'chart/chartspace.pyi', 'chart/data_source.pyi', 'chart/descriptors.pyi', 'chart/error_bar.pyi', 'chart/label.pyi', 'chart/layout.pyi', 'chart/legend.pyi', 'chart/line_chart.pyi', 'chart/marker.pyi', 'chart/picture.pyi', 'chart/pie_chart.pyi', 'chart/pivot.pyi', 'chart/plotarea.pyi', 'chart/print_settings.pyi', 'chart/radar_chart.pyi', 'chart/reader.pyi', 'chart/reference.pyi', 'chart/scatter_chart.pyi', 'chart/series.pyi', 'chart/series_factory.pyi', 'chart/shapes.pyi', 'chart/stock_chart.pyi', 'chart/surface_chart.pyi', 'chart/text.pyi', 'chart/title.pyi', 'chart/trendline.pyi', 'chart/updown_bars.pyi', 'chartsheet/__init__.pyi', 'chartsheet/chartsheet.pyi', 'chartsheet/custom.pyi', 'chartsheet/properties.pyi', 'chartsheet/protection.pyi', 'chartsheet/publish.pyi', 'chartsheet/relation.pyi', 'chartsheet/views.pyi', 'comments/__init__.pyi', 'comments/author.pyi', 'comments/comment_sheet.pyi', 'comments/comments.pyi', 'comments/shape_writer.pyi', 'compat/__init__.pyi', 'compat/abc.pyi', 'compat/numbers.pyi', 'compat/product.pyi', 'compat/singleton.pyi', 'compat/strings.pyi', 'descriptors/__init__.pyi', 'descriptors/base.pyi', 'descriptors/excel.pyi', 'descriptors/namespace.pyi', 'descriptors/nested.pyi', 'descriptors/sequence.pyi', 'descriptors/serialisable.pyi', 'descriptors/slots.pyi', 'drawing/__init__.pyi', 'drawing/colors.pyi', 'drawing/connector.pyi', 'drawing/drawing.pyi', 'drawing/effect.pyi', 'drawing/fill.pyi', 'drawing/geometry.pyi', 'drawing/graphic.pyi', 'drawing/image.pyi', 'drawing/line.pyi', 'drawing/picture.pyi', 'drawing/properties.pyi', 'drawing/relation.pyi', 'drawing/spreadsheet_drawing.pyi', 'drawing/text.pyi', 'drawing/xdr.pyi', 'formatting/__init__.pyi', 'formatting/formatting.pyi', 'formatting/rule.pyi', 'formula/__init__.pyi', 'formula/tokenizer.pyi', 'formula/translate.pyi', 'packaging/__init__.pyi', 'packaging/core.pyi', 'packaging/extended.pyi', 'packaging/interface.pyi', 'packaging/manifest.pyi', 'packaging/relationship.pyi', 'packaging/workbook.pyi', 'pivot/__init__.pyi', 'pivot/cache.pyi', 'pivot/fields.pyi', 'pivot/record.pyi', 'pivot/table.pyi', 'reader/__init__.pyi', 'reader/drawings.pyi', 'reader/excel.pyi', 'reader/strings.pyi', 'reader/workbook.pyi', 'styles/__init__.pyi', 'styles/alignment.pyi', 'styles/borders.pyi', 'styles/builtins.pyi', 'styles/cell_style.pyi', 'styles/colors.pyi', 'styles/differential.pyi', 'styles/fills.pyi', 'styles/fonts.pyi', 'styles/named_styles.pyi', 'styles/numbers.pyi', 'styles/protection.pyi', 'styles/proxy.pyi', 'styles/styleable.pyi', 'styles/stylesheet.pyi', 'styles/table.pyi', 'utils/__init__.pyi', 'utils/bound_dictionary.pyi', 'utils/cell.pyi', 'utils/dataframe.pyi', 'utils/datetime.pyi', 'utils/escape.pyi', 'utils/exceptions.pyi', 'utils/formulas.pyi', 'utils/indexed_list.pyi', 'utils/inference.pyi', 'utils/protection.pyi', 'utils/units.pyi', 'workbook/__init__.pyi', 'workbook/_writer.pyi', 'workbook/child.pyi', 'workbook/defined_name.pyi', 'workbook/external_link/__init__.pyi', 'workbook/external_link/external.pyi', 'workbook/external_reference.pyi', 'workbook/function_group.pyi', 'workbook/properties.pyi', 'workbook/protection.pyi', 'workbook/smart_tags.pyi', 'workbook/views.pyi', 'workbook/web.pyi', 'workbook/workbook.pyi', 'worksheet/__init__.pyi', 'worksheet/_read_only.pyi', 'worksheet/_reader.pyi', 'worksheet/_write_only.pyi', 'worksheet/_writer.pyi', 'worksheet/cell_range.pyi', 'worksheet/cell_watch.pyi', 'worksheet/controls.pyi', 'worksheet/copier.pyi', 'worksheet/custom.pyi', 'worksheet/datavalidation.pyi', 'worksheet/dimensions.pyi', 'worksheet/drawing.pyi', 'worksheet/errors.pyi', 'worksheet/filters.pyi', 'worksheet/header_footer.pyi', 'worksheet/hyperlink.pyi', 'worksheet/merge.pyi', 'worksheet/ole.pyi', 'worksheet/page.pyi', 'worksheet/pagebreak.pyi', 'worksheet/picture.pyi', 'worksheet/properties.pyi', 'worksheet/protection.pyi', 'worksheet/related.pyi', 'worksheet/scenario.pyi', 'worksheet/smart_tag.pyi', 'worksheet/table.pyi', 'worksheet/views.pyi', 'worksheet/worksheet.pyi', 'writer/__init__.pyi', 'writer/excel.pyi', 'writer/theme.pyi', 'xml/__init__.pyi', 'xml/constants.pyi', 'xml/functions.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
