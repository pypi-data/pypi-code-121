import json
import Famcy

class table_block(Famcy.FamcyBlock):
    """
    Represents the block to display
    table_block. 
    """
    def __init__(self, **kwargs):
        self.value = table_block.generate_template_content()
        super(table_block, self).__init__(**kwargs)
        self.init_block()

    @classmethod
    def generate_template_content(cls, fblock_type=None):
        """
        This is the function that
        returns the template content 
        for the given fblock. 
        - Return a content dictionary
        """
        return {
            "input_button": "radio",                     # ("checkbox" / "radio" / "none")
            "input_value_col_field": "col_title2",          # if input_button != "none"

            "page_detail": True,                            # (true / false)
            "page_detail_content": "key_value",             # if page_detail == true: (key_value / HTML_STR => ["<p>line1</p>", "<p>line2</p>"])

            "toolbar": True,                                # (true / false)
            "page_footer": True,                            # (true / false)
            "page_footer_detail": {                         # if page_footer == true
                "page_size": 1,
                "page_list": [1, 2, "all"]
            },

            "table_height": "200px",

            "column": [[{
                    "title": 'col_title1 name',
                    "field": 'col_title1',
                    "rowspan": 1,
                    "align": 'center',
                    "valign": 'middle',
                    "sortable": True
                },
                {
                    "title": 'col_title1 name',
                    "field": 'col_title2',
                    "rowspan": 1,
                    "align": 'center',
                    "valign": 'middle',
                    "sortable": True
                },
                {
                    "title": 'col_title1 name',
                    "field": 'col_title3',
                    "rowspan": 1,
                    "align": 'center',
                    "valign": 'middle',
                    "sortable": True
                }
            ]],
            "data": [
                {
                    "col_title2": "1",
                    "col_title1": "row_content12",
                    "col_title3": "row_content13",
                    "col_title4": "row_content13"
                },
                {
                    "col_title1": "2",
                    "col_title2": "row_content22",
                    "col_title3": "row_content23"
                },
                {
                    "col_title1": "3",
                    "col_title2": "row_content32",
                    "col_title3": "row_content33"
                },
                {
                    "col_title1": "4",
                    "col_title2": "row_content12",
                    "col_title3": "row_content13"
                },
                {
                    "col_title1": "5",
                    "col_title2": "row_content22",
                    "col_title3": "row_content23"
                },
                {
                    "col_title1": "6",
                    "col_title2": "row_content32",
                    "col_title3": "row_content33"
                },
                {
                    "col_title1": "7",
                    "col_title2": "row_content12",
                    "col_title3": "row_content13"
                },
                {
                    "col_title1": "8",
                    "col_title2": "row_content22",
                    "col_title3": "row_content23"
                },
                {
                    "col_title1": "9",
                    "col_title2": "row_content32",
                    "col_title3": "row_content33"
                },{
                    "col_title2": "10",
                    "col_title1": "row_content12",
                    "col_title3": "row_content13",
                    "col_title4": "row_content13"
                },
                {
                    "col_title1": "11",
                    "col_title2": "row_content22",
                    "col_title3": "row_content23"
                },
                {
                    "col_title1": "12",
                    "col_title2": "row_content32",
                    "col_title3": "row_content33"
                },
                {
                    "col_title1": "13",
                    "col_title2": "row_content12",
                    "col_title3": "row_content13"
                },
                {
                    "col_title1": "14",
                    "col_title2": "row_content22",
                    "col_title3": "row_content23"
                },
                {
                    "col_title1": "15",
                    "col_title2": "row_content32",
                    "col_title3": "row_content33"
                },
                {
                    "col_title1": "16",
                    "col_title2": "row_content12",
                    "col_title3": "row_content13"
                },
                {
                    "col_title1": "17",
                    "col_title2": "row_content22",
                    "col_title3": "row_content23"
                },
                {
                    "col_title1": "18",
                    "col_title2": "row_content32",
                    "col_title3": "row_content33"
                },{
                    "col_title2": "19",
                    "col_title1": "row_content12",
                    "col_title3": "row_content13",
                    "col_title4": "row_content13"
                },
                {
                    "col_title1": "20",
                    "col_title2": "row_content22",
                    "col_title3": "row_content23"
                },
                {
                    "col_title1": "21",
                    "col_title2": "row_content32",
                    "col_title3": "row_content33"
                },
                {
                    "col_title1": "22",
                    "col_title2": "row_content12",
                    "col_title3": "row_content13"
                },
                {
                    "col_title1": "23",
                    "col_title2": "row_content22",
                    "col_title3": "row_content23"
                },
                {
                    "col_title1": "24",
                    "col_title2": "row_content32",
                    "col_title3": "row_content33"
                },
                {
                    "col_title1": "25",
                    "col_title2": "row_content12",
                    "col_title3": "row_content13"
                },
                {
                    "col_title1": "26",
                    "col_title2": "row_content22",
                    "col_title3": "row_content23"
                },
                {
                    "col_title1": "27",
                    "col_title2": "row_content32",
                    "col_title3": "row_content33"
                }
            ]
        }

    def generate_table(self):
        # generate column title
        _head = Famcy.thead()

        column_dict = {}
        for t in self.value["column"]:
            _tr = Famcy.tr()

            # generate btn
            _thb = Famcy.th()
            _thd = Famcy.div()
            _thd["className"] = "th-inner"

            if self.value["input_button"] == "checkbox":
                _thb.style["text-align"] = 'center'
                _thb.style["vertical-align"] = 'middle'
                _thb["rowspan"] = "1"
                _thb["data-field"] = "state"

                _thl = Famcy.label()

                _thi = Famcy.input()
                _thi["name"] = str(self.name)
                _thi["type"] = self.value["input_button"]
                _thi["onclick"] = "select_all(this, 'tbody" + self.id + "')"
                _ths = Famcy.span()

                _thl.addElement(_thi)
                _thl.addElement(_ths)
                _thd.addElement(_thl)
            _thb.addElement(_thd)
            _tr.addElement(_thb)

            for c in t:
                column_dict[c["field"]] = c

                _th = Famcy.th()
                _th.style["text-align"] = c["align"]
                _th.style["vertical-align"] = c["valign"]
                _th["rowspan"] = str(c["rowspan"])
                _th["data-field"] = c["field"]
                _div = Famcy.div()
                _div.innerHTML = str(c["title"])
                _div["className"] = "th-inner"
                if c["sortable"]:
                    _div["className"] = "sortable"
                    _div["className"] = "both"

                _th.addElement(_div)
                _tr.addElement(_th)

            _head.addElement(_tr)

        # generate body info
        _body = Famcy.tbody()
        _body["id"] = "tbody"+self.id
        for i, d in enumerate(self.value["data"]):
            _tr = Famcy.tr()
            _tr["className"] = "display_none"
            _tr["data-index"] = str(i)
            _tr["data-has-detail-view"] = "false"

            # generate btn
            if self.value["input_button"] == "checkbox" or self.value["input_button"] == "radio":
                _tdb = Famcy.td()
                _tdb.style["text-align"] = 'center'
                _tdb.style["vertical-align"] = 'middle'
                _tdb["rowspan"] = "1"
                _tdb["data-field"] = "state"

                _tdl = Famcy.label()

                _tdi = Famcy.input()
                _tdi["className"] = "table_btn"
                _tdi["name"] = str(self.name)
                _tdi["type"] = self.value["input_button"]
                _tdi["data-index"] = str(i)
                _ = ""
                if isinstance(self.value["input_value_col_field"], list):
                    for f in self.value["input_value_col_field"]:
                        _ += d[f] + ","
                else:
                    _ = d[self.value["input_value_col_field"]] + " "
                _tdi["value"] = _[:-1]
                _tds = Famcy.span()

                _tdl.addElement(_tdi)
                _tdl.addElement(_tds)
                _tdb.addElement(_tdl)
                _tr.addElement(_tdb)

            for k in column_dict.keys():
                _td = Famcy.td()
                _td.style["text-align"] = column_dict[k]["align"]
                _td.style["vertical-align"] = column_dict[k]["valign"]
                _td["data-field"] = column_dict[k]["field"]
                _td.innerHTML = str(d[k]) if k in d.keys() else ""
                _tr.addElement(_td)

            _body.addElement(_tr)

        # display first page
        page_size = self.value["page_footer_detail"]["page_size"] if isinstance(self.value["page_footer_detail"]["page_size"], int) else len(data)
        for x in range(page_size):
            if len(_body.children) > x:
                _body.children[x].classList.remove("display_none")

        if self.value["page_footer"]:
            _h3 = Famcy.h3()
            _h3.innerHTML = "每頁顯示資料數: "
            self.body.children[2].addElement(_h3)

            for p in self.value["page_footer_detail"]["page_list"]:
                _b = Famcy.button()
                _b.innerHTML = str(p)
                _b["className"] = "pageBtn"
                _b["onclick"] = "go_to_page('" + str(p) + "', '" + self.id + "')"
                self.body.children[2].addElement(_b)

            # switch page section html
            _div = Famcy.div()
            _div["className"] = "switch_page_holder"
            _div["id"] = "switch_page"+self.id
            _div["page_size"] = str(page_size)
            _pbtn = Famcy.button()
            _pbtn["onclick"] = "go_to_previous_page('" + self.id + "')"
            _pbtn.innerHTML = "<"
            _page_num = Famcy.h3()
            _page_num.innerHTML = "1"
            _nbtn = Famcy.button()
            _nbtn["onclick"] = "go_to_next_page('" + self.id + "')"
            _nbtn.innerHTML = ">"
            _div.addElement(_pbtn)
            _div.addElement(_page_num)
            _div.addElement(_nbtn)
            self.body.children[2].addElement(_div)

        self.body.children[1].addElement(_head)
        self.body.children[1].addElement(_body)

        self.body.style["height"] = self.value["table_height"]
        self.body.style["overflow"] = "auto"

    def init_block(self):
        self.header_script += """
        <!--table-->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.6.3/css/all.css" integrity="sha384-UHRtZLI+pbxtHCWp1t77Bi1L4ZtiqrqD80Kn4Z8NTSRyMA2Fd33n5dQ8lWUE00s/" crossorigin="anonymous">
        <link rel="stylesheet" href="https://unpkg.com/bootstrap-table@1.18.3/dist/bootstrap-table.min.css">
        <link href="https://unpkg.com/bootstrap-table@1.18.3/dist/bootstrap-table.min.css" rel="stylesheet">
        <script src="https://unpkg.com/tableexport.jquery.plugin/tableExport.min.js"></script>
        <script src="https://unpkg.com/bootstrap-table@1.18.3/dist/bootstrap-table.min.js"></script>
        <script src="https://unpkg.com/bootstrap-table@1.18.3/dist/bootstrap-table-locale-all.min.js"></script>
        <script src="https://unpkg.com/bootstrap-table@1.18.3/dist/extensions/export/bootstrap-table-export.min.js"></script>
        """
        self.body = Famcy.div()
        self.body["className"] = "table_holder"
        self.body["id"] = self.id

        toolbar_temp = Famcy.div()
        toolbar_temp["id"] = "toolbar_" + self.id

        table_temp = Famcy.table()
        table_temp["id"] = "table_" + self.id

        footer = Famcy.div()
        footer["className"] = "table_footer"

        self.body.addElement(toolbar_temp)
        self.body.addElement(table_temp)
        self.body.addElement(footer)

        static_script = Famcy.script()
        static_script["src"] = "/static/js/table_page.js"
        self.body.addStaticScript(static_script, position="head")

    def render_inner(self):
        # remove previous data
        self.body.children[1].children = []
        self.body.children[2].children = []

        self.generate_table()
        return self.body