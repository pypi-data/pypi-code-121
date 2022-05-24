# -*- coding: utf-8 -*-
# Copyright (c) 2020-2021 Salvador E. Tropea
# Copyright (c) 2020-2021 Instituto Nacional de Tecnología Industrial
# Copyright (c) 2016-2020 Oliver Henry Walters (@SchrodingersGat)
# License: MIT
# Project: KiBot (formerly KiPlot)
# Adapted from: https://github.com/SchrodingersGat/KiBoM
"""
HTML Writer: Generates a HTML BoM file.
"""
import os
from base64 import b64encode
from struct import unpack
from .columnlist import ColumnList, BoMError
from .kibot_logo import KIBOT_LOGO, KIBOT_LOGO_W, KIBOT_LOGO_H

BG_GEN = "#DCF5E4"
BG_KICAD = "#F5DCA9"
BG_USER = "#DCEFF5"
BG_EMPTY = "#F57676"
BG_GEN_L = "#E6FFEE"
BG_KICAD_L = "#FFE6B3"
BG_USER_L = "#E6F9FF"
BG_EMPTY_L = "#FF8080"
HEAD_COLOR_R = "#982020"
HEAD_COLOR_R_L = "#c85050"
HEAD_COLOR_G = "#009879"
HEAD_COLOR_G_L = "#30c8a9"
HEAD_COLOR_B = "#0e4e8e"
HEAD_COLOR_B_L = "#3e7ebe"
STYLE_COMMON = (" .cell-title { vertical-align: bottom; }\n"
                " .cell-info { vertical-align: top; padding: 1em;}\n"
                " .cell-extra-info { vertical-align: top; padding: 1em;}\n"
                " .cell-stats { vertical-align: top; padding: 1em;}\n"
                " .title { font-size:2.5em; font-weight: bold; }\n"
                " .subtitle { font-size:1.5em; font-weight: bold; }\n"
                " .h2 { font-size:1.5em; font-weight: bold; }\n"
                " .td-empty0 { text-align: center; background-color: "+BG_EMPTY+";}\n"
                " .td-gen0 { text-align: center; background-color: "+BG_GEN+";}\n"
                " .td-kicad0 { text-align: center; background-color: "+BG_KICAD+";}\n"
                " .td-user0 { text-align: center; background-color: "+BG_USER+";}\n"
                " .td-empty1 { text-align: center; background-color: "+BG_EMPTY_L+";}\n"
                " .td-gen1 { text-align: center; background-color: "+BG_GEN_L+";}\n"
                " .td-kicad1 { text-align: center; background-color: "+BG_KICAD_L+";}\n"
                " .td-user1 { text-align: center; background-color: "+BG_USER_L+";}\n"
                " .color-ref { margin: 25px 0; }\n"
                " .color-ref th { text-align: left }\n"
                " .color-ref td { padding: 5px 20px; }\n"
                " .head-table { margin-bottom: 2em; }\n"
                # Table sorting cursor. 60% transparent when disabled. Solid white when enabled.
                " .tg-sort-header::-moz-selection{background:0 0}\n"
                " .tg-sort-header::selection{background:0 0}.tg-sort-header{cursor:pointer}\n"
                " .tg-sort-header:after{content:'';float:right;border-width:0 5px 5px;border-style:solid;\n"
                "                       border-color:#ffffff transparent;visibility:hidden;opacity:.6}\n"
                " .tg-sort-header:hover:after{visibility:visible}\n"
                " .tg-sort-asc:after,.tg-sort-asc:hover:after,.tg-sort-desc:after{visibility:visible;opacity:1}\n"
                " .tg-sort-desc:after{border-bottom:none;border-width:5px 5px 0}\n")
TABLE_MODERN = """
 .content-table {
   border-collapse:
   collapse;
   margin-top: 5px;
   margin-bottom: 4em;
   font-size: 0.9em;
   font-family: sans-serif;
   min-width: 400px;
   border-radius: 5px 5px 0 0;
   overflow: hidden;
   box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
 }
 .content-table thead tr { background-color: @bg@; color: #ffffff; text-align: left; }
 .content-table th, .content-table td { padding: 12px 15px; }
 .content-table tbody tr { border-bottom: 1px solid #dddddd; }
 .content-table tbody tr:nth-of-type(even) { background-color: #f3f3f3; }
 .content-table tbody tr:last-of-type { border-bottom: 2px solid @bg@; }
 .content-table * tr:hover > td { background-color: @bgl@ !important }
"""
TABLE_CLASSIC = (" .content-table, .content-table th, .content-table td { border: 1px solid black; }\n"
                 " .content-table * tr:hover > td { background-color: #B0B0B0 !important }\n")
# JavaScript table sorter. Is floating around internet, i.e.:
# - Stack Overflow: https://stackoverflow.com/questions/61122696/addeventlistener-after-change-event
# - pimpmykicadbom: https://gitlab.com/antto/pimpmykicadbom
# - Table Generator: https://www.tablesgenerator.com/
SORT_CODE = ('<script charset="utf-8">\n'
             '  var TGSort = window.TGSort || function(n) {\n'
             '    "use strict";\n'
             '    function r(n) { return n ? n.length : 0 }\n'
             '    function t(n, t, e, o = 0) { for (e = r(n); o < e; ++o) t(n[o], o) }\n'
             '    function e(n) { return n.split("").reverse().join("") }\n'
             '    function o(n) {\n'
             '      var e = n[0];\n'
             '      return t(n, function(n) {\n'
             '        for (; !n.startsWith(e);) e = e.substring(0, r(e) - 1)\n'
             '      }), r(e)\n'
             '    }\n'
             '    function u(n, r, e = []) {\n'
             '      return t(n, function(n) {\n'
             '        r(n) && e.push(n)\n'
             '      }), e\n'
             '    }\n'
             '    var a = parseFloat;\n'
             '    function i(n, r) {\n'
             '      return function(t) {\n'
             '        var e = "";\n'
             '        return t.replace(n, function(n, t, o) {\n'
             '          return e = t.replace(r, "") + "." + (o || "").substring(1)\n'
             '        }), a(e)\n'
             '      }\n'
             '    }\n'
             r'    var s = i(/^(?:\s*)([+-]?(?:\d+)(?:,\d{3})*)(\.\d*)?$/g, /,/g),''\n'
             r'      c = i(/^(?:\s*)([+-]?(?:\d+)(?:\.\d{3})*)(,\d*)?$/g, /\./g);''\n'
             '    function f(n) {\n'
             '      var t = a(n);\n'
             '      return !isNaN(t) && r("" + t) + 1 >= r(n) ? t : NaN\n'
             '    }\n'
             '    function d(n) {\n'
             '      var e = [],\n'
             '        o = n;\n'
             '      return t([f, s, c], function(u) {\n'
             '        var a = [],\n'
             '          i = [];\n'
             '        t(n, function(n, r) {\n'
             '          r = u(n), a.push(r), r || i.push(n)\n'
             '        }), r(i) < r(o) && (o = i, e = a)\n'
             '      }), r(u(o, function(n) {\n'
             '        return n == o[0]\n'
             '      })) == r(o) ? e : []\n'
             '    }\n'
             '    function v(n) {\n'
             '      if ("TABLE" == n.nodeName) {\n'
             '        for (var a = function(r) {\n'
             '            var e, o, u = [],\n'
             '              a = [];\n'
             '            return function n(r, e) {\n'
             '              e(r), t(r.childNodes, function(r) {\n'
             '                n(r, e)\n'
             '              })\n'
             '            }(n, function(n) {\n'
             '              "TR" == (o = n.nodeName) ? (e = [], u.push(e), a.push(n)) : "TD" != o && "TH" != o || e.push(n)\n'  # noqa: E501
             '            }), [u, a]\n'
             '          }(), i = a[0], s = a[1], c = r(i), f = c > 1 && r(i[0]) < r(i[1]) ? 1 : 0, v = f + 1, p = i[f], h = r(p), l = [], g = [], N = [], m = v; m < c; ++m) {\n'  # noqa: E501
             '          for (var T = 0; T < h; ++T) {\n'
             '            r(g) < h && g.push([]);\n'
             '            var C = i[m][T],\n'
             '              L = C.textContent || C.innerText || "";\n'
             '            g[T].push(L.trim())\n'
             '          }\n'
             '          N.push(m - v)\n'
             '        }\n'
             '        t(p, function(n, t) {\n'
             '          l[t] = 0;\n'
             '          var a = n.classList;\n'
             '          a.add("tg-sort-header"), n.addEventListener("click", function() {\n'
             '            var n = l[t];\n'
             '            ! function() {\n'
             '              for (var n = 0; n < h; ++n) {\n'
             '                var r = p[n].classList;\n'
             '                r.remove("tg-sort-asc"), r.remove("tg-sort-desc"), l[n] = 0\n'
             '              }\n'
             '            }(), (n = 1 == n ? -1 : +!n) && a.add(n > 0 ? "tg-sort-asc" : "tg-sort-desc"), l[t] = n;\n'
             '            var i, f = g[t],\n'
             '              m = function(r, t) {\n'
             '                return n * f[r].localeCompare(f[t]) || n * (r - t)\n'
             '              },\n'
             '              T = function(n) {\n'
             '                var t = d(n);\n'
             '                if (!r(t)) {\n'
             '                  var u = o(n),\n'
             '                    a = o(n.map(e));\n'
             '                  t = d(n.map(function(n) {\n'
             '                    return n.substring(u, r(n) - a)\n'
             '                  }))\n'
             '                }\n'
             '                return t\n'
             '              }(f);\n'
             '            (r(T) || r(T = r(u(i = f.map(Date.parse), isNaN)) ? [] : i)) && (m = function(r, t) {\n'
             '              var e = T[r],\n'
             '                o = T[t],\n'
             '                u = isNaN(e),\n'
             '                a = isNaN(o);\n'
             '              return u && a ? 0 : u ? -n : a ? n : e > o ? n : e < o ? -n : n * (r - t)\n'
             '            });\n'
             '            var C, L = N.slice();\n'
             '            L.sort(m);\n'
             '            for (var E = v; E < c; ++E)(C = s[E].parentNode).removeChild(s[E]);\n'
             '            for (E = v; E < c; ++E) C.appendChild(s[v + L[E - v]])\n'
             '          })\n'
             '        })\n'
             '      }\n'
             '    }\n'
             '    n.addEventListener("DOMContentLoaded", function() {\n'
             '      for (var t = n.getElementsByClassName("content-table"), e = 0; e < r(t); ++e) try {\n'
             '        v(t[e])\n'
             '      } catch (n) {}\n'
             '    })\n'
             '  }(document)\n'
             '</script>\n')


def cell_class(col):
    """ Return a background color for a given column title """
    col = col.lower()
    # Auto-generated columns
    if col in ColumnList.COLUMNS_GEN_L:
        return 'gen'  # BG_GEN
    # KiCad protected columns
    elif col in ColumnList.COLUMNS_PROTECTED_L:
        return 'kicad'  # BG_KICAD
    # Additional user columns
    return 'user'  # BG_USER


def link(text):
    for t in ["http", "https", "ftp", "www"]:
        if text.startswith(t):
            return '<a href="{t}">{t}</a>'.format(t=text)
    return text


def content_table(html, groups, headings, head_names, cfg, link_datasheet, link_digikey, col_colors, dnf=False):
    cl = ''
    # Table start
    html.write('<table class="content-table">\n')
    # Row titles:
    html.write(" <thead>\n")
    html.write("  <tr>\n")
    for i, h in enumerate(head_names):
        if col_colors:
            # Cell background color
            cl = ' class="th-'+cell_class(headings[i])+'"'
        html.write('   <th{}>{}</th>\n'.format(cl, h))
    html.write("  </tr>\n")
    html.write(" </thead>\n")

    html.write(" <tbody>\n")
    rc = 0
    hl_empty = cfg.html.highlight_empty
    for i, group in enumerate(groups):
        if (cfg.ignore_dnf and not group.is_fitted()) != dnf:
            continue
        row = group.get_row(headings)
        if link_datasheet != -1:
            datasheet = group.get_field(ColumnList.COL_DATASHEET_L)
        html.write('  <tr id="{}">\n'.format(i))
        for n, r in enumerate(row):
            # A link to Digi-Key?
            if link_digikey and headings[n] in link_digikey:
                r = '<a href="http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail&name=' + r + '">' + r + '</a>'
            # Link this column to the datasheet?
            if link_datasheet == n and datasheet.startswith('http'):
                r = '<a href="' + datasheet + '">' + r + '</a>'
            if col_colors:
                # Empty cell?
                if hl_empty and (len(r) == 0 or r.strip() == "~"):
                    cl = 'empty'
                else:
                    cl = cell_class(headings[n])
                cl = ' class="td-{}{}"'.format(cl, rc % 2)
            if headings[n] == ColumnList.COL_REFERENCE_L:
                for ref in r.split(cfg.ref_separator):
                    r = '<div id="{}"></div>'.format(ref)+r
            html.write('   <td{}>{}</td>\n'.format(cl, link(r)))
        html.write("  </tr>\n")
        rc += 1
    html.write(" </tbody>\n")
    html.write("</table>\n")
    return


def embed_image(file):
    with open(file, 'rb') as f:
        s = f.read()
    if not (s[:8] == b'\x89PNG\r\n\x1a\n' and (s[12:16] == b'IHDR')):
        raise BoMError('Only PNG images are supported for the logo')
    w, h = unpack('>LL', s[16:24])
    return int(w), int(h), 'data:image/png;base64,'+b64encode(s).decode('ascii')


def write_stats(html, cfg):
    if len(cfg.aggregate) == 1:
        # Only one project
        html.write('<tr>\n')
        html.write(' <td class="cell-info">\n')
        if not cfg.html.hide_pcb_info:
            prj = cfg.aggregate[0]
            html.write("   <b>Schematic</b>: {}<br>\n".format(prj.name))
            html.write("   <b>Variant</b>: {}<br>\n".format(cfg.variant.name))
            html.write("   <b>Revision</b>: {}<br>\n".format(prj.sch.revision))
            html.write("   <b>Date</b>: {}<br>\n".format(prj.sch.date))
            html.write("   <b>KiCad Version</b>: {}<br>\n".format(cfg.kicad_version))
        html.write(' </td>\n')
        html.write(' <td class="cell-stats">\n')
        if not cfg.html.hide_stats_info:
            html.write("   <b>Component Groups</b>: {}<br>\n".format(cfg.n_groups))
            html.write("   <b>Component Count</b>: {} (per PCB)<br>\n\n".format(cfg.total_str))
            html.write("   <b>Fitted Components</b>: {} (per PCB)<br>\n".format(cfg.fitted_str))
            html.write("   <b>Number of PCBs</b>: {}<br>\n".format(cfg.number))
            html.write("   <b>Total Components</b>: {t} (for {n} PCBs)<br>\n".format(n=cfg.number, t=cfg.n_build))
        html.write(' </td>\n')
        html.write('</tr>\n')
    else:
        # Multiple projects
        # Global stats
        html.write('<tr>\n')
        html.write(' <td class="cell-info">\n')
        if not cfg.html.hide_pcb_info:
            html.write("   <b>Variant</b>: {}<br>\n".format(cfg.variant.name))
            html.write("   <b>KiCad Version</b>: {}<br>\n".format(cfg.kicad_version))
        html.write(' </td>\n')
        html.write(' <td class="cell-stats">\n')
        if not cfg.html.hide_stats_info:
            html.write("   <b>Component Groups</b>: {}<br>\n".format(cfg.n_groups))
            html.write("   <b>Component Count</b>: {} (per PCB)<br>\n\n".format(cfg.total_str))
            html.write("   <b>Fitted Components</b>: {} (per PCB)<br>\n".format(cfg.fitted_str))
            html.write("   <b>Number of PCBs</b>: {}<br>\n".format(cfg.number))
            html.write("   <b>Total Components</b>: {t} (for {n} PCBs)<br>\n".format(n=cfg.number, t=cfg.n_build))
        html.write(' </td>\n')
        html.write('</tr>\n')
        # Individual stats
        for prj in cfg.aggregate:
            html.write('<tr>\n')
            html.write(' <td colspan="2" class="cell-title">\n')
            html.write('  <div class="subtitle">'+prj.sch.title+'</div>\n')
            html.write(' </td>\n')
            html.write('</tr>\n')
            html.write('<tr>\n')
            html.write(' <td class="cell-info">\n')
            if not cfg.html.hide_pcb_info:
                html.write("   <b>Schematic</b>: {}<br>\n".format(prj.name))
                html.write("   <b>Revision</b>: {}<br>\n".format(prj.sch.revision))
                html.write("   <b>Date</b>: {}<br>\n".format(prj.sch.date))
                if prj.sch.company:
                    html.write("   <b>Company</b>: {}<br>\n".format(prj.sch.company))
                if prj.ref_id:
                    html.write("   <b>ID</b>: {}<br>\n".format(prj.ref_id))
            html.write(' </td>\n')
            html.write(' <td class="cell-stats">\n')
            if not cfg.html.hide_stats_info:
                html.write("   <b>Component Groups</b>: {}<br>\n".format(prj.comp_groups))
                html.write("   <b>Component Count</b>: {} (per PCB)<br>\n\n".format(prj.total_str))
                html.write("   <b>Fitted Components</b>: {} (per PCB)<br>\n".format(prj.fitted_str))
                html.write("   <b>Number of PCBs</b>: {}<br>\n".format(prj.number))
                html.write("   <b>Total Components</b>: {t} (for {n} PCBs)<br>\n".format(n=prj.number, t=prj.comp_build))
            html.write(' </td>\n')
            html.write('</tr>\n')


def write_extra_info(html, cfg):
    if not cfg.html.extra_info:
        return
    html.write('<tr>\n')
    html.write(' <td colspan="2" class="cell-extra-info">\n')
    for e in cfg.html.extra_info:
        html.write("   <b>{}</b><br>\n".format(e))
    html.write(' </td>\n')
    html.write('</tr>\n')


def write_html(filename, groups, headings, head_names, cfg):
    """
    Write BoM out to a HTML file
    filename = path to output file (must be a .csv, .txt or .tsv file)
    groups = [list of ComponentGroup groups]
    headings = [list of headings to search for data in the BoM file]
    head_names = [list of headings to display in the BoM file]
    cfg = BoMOptions object with all the configuration
    """
    link_datasheet = -1
    if cfg.html.datasheet_as_link and cfg.html.datasheet_as_link in headings:
        link_datasheet = headings.index(cfg.html.datasheet_as_link)
    link_digikey = cfg.html.digikey_link
    col_colors = cfg.html.col_colors
    # Compute the CSS
    style_name = cfg.html.style
    if os.path.isfile(style_name):
        with open(style_name, 'rt') as f:
            style = f.read()
    else:
        # Common stuff
        style = STYLE_COMMON
        if style_name.startswith('modern-'):
            # content-table details
            if style_name.endswith('green'):
                head_color = HEAD_COLOR_G
                head_color_l = HEAD_COLOR_G_L
            elif style_name.endswith('blue'):
                head_color = HEAD_COLOR_B
                head_color_l = HEAD_COLOR_B_L
            else:
                head_color = HEAD_COLOR_R
                head_color_l = HEAD_COLOR_R_L
            style += TABLE_MODERN.replace('@bg@', head_color)
            style += TABLE_MODERN.replace('@bgl@', head_color_l)
        else:
            # Background is white, so we change the sorting cursor to black
            style = style.replace('border-color:#ffffff', 'border-color:#000000')
            style += TABLE_CLASSIC

    with open(filename, "w") as html:
        # HTML Head
        html.write("<html>\n")
        html.write("<head>\n")
        html.write(' <meta charset="UTF-8">\n')  # UTF-8 encoding for unicode support
        if cfg.html.title:
            html.write(' <title>'+cfg.html.title+'</title>\n')
        # CSS
        html.write("<style>\n")
        html.write(style)
        html.write("</style>\n")
        html.write("</head>\n")

        html.write("<body>\n")
        # Page Header
        img = None
        if cfg.html.logo is not None:
            if cfg.html.logo:
                img_w, img_h, img = embed_image(cfg.html.logo)
            else:
                img = 'data:image/png;base64,'+KIBOT_LOGO
                img_w = KIBOT_LOGO_W
                img_h = KIBOT_LOGO_H
        if img or not cfg.html.hide_pcb_info or not cfg.html.hide_stats_info or cfg.html.title:
            html.write('<table class="head-table">\n')
            html.write('<tr>\n')
            n = 2
            if len(cfg.aggregate) > 1:
                n += 2*len(cfg.aggregate)
            if len(cfg.html.extra_info):
                n += 1
            html.write(' <td rowspan="{}">\n'.format(n))
            if img:
                html.write('  <img src="'+img+'" alt="Logo" width="'+str(img_w)+'" height="'+str(img_h)+'">\n')
            html.write(' </td>\n')
            html.write(' <td colspan="2" class="cell-title">\n')
            if cfg.html.title:
                html.write('  <div class="title">'+cfg.html.title+'</div>\n')
            html.write(' </td>\n')
            html.write('</tr>\n')
            write_extra_info(html, cfg)
            write_stats(html, cfg)
            html.write('</table>\n')

        # Fitted groups
        html.write("<h2>Component Groups</h2>\n")
        content_table(html, groups, headings, head_names, cfg, link_datasheet, link_digikey, col_colors)

        # DNF component groups
        if cfg.html.generate_dnf and cfg.n_total != cfg.n_fitted:
            html.write("<h2>Optional components (DNF=Do Not Fit)</h2>\n")
            content_table(html, groups, headings, head_names, cfg, link_datasheet, link_digikey, col_colors, True)

        # Color reference
        if col_colors:
            html.write('<table class="color-ref">\n')
            html.write('<tr><th>Color reference:</th></tr>\n')
            html.write('<tr><td class="td-kicad0">KiCad Fields (default)</td></tr>\n')
            html.write('<tr><td class="td-gen0">Generated Fields</td></tr>\n')
            html.write('<tr><td class="td-user0">User Fields</td></tr>\n')
            if cfg.html.highlight_empty:
                html.write('<tr><td class="td-empty0">Empty Fields</td></tr>\n')
            html.write('</table>\n')

        html.write(SORT_CODE)
        html.write("</body></html>")

    return True
