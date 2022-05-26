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
                }
            ]
        }

    def generate_table(self):
        self.radio_num = 1 if self.value["input_button"] and self.value["input_button"] != "none" else 0
        _head = self.generate_head()
        _body = self.generate_body()

        # display first page
        self.value["page_footer_detail"]["page_size"] = page_size = self.value["page_footer_detail"]["page_size"] if isinstance(self.value["page_footer_detail"]["page_size"], int) else len(data)
        self.display_page(_body, page_size)

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

    def display_page(self, _body, page_size):
        for x in range(page_size):
            if len(_body.children) > x:
                if "display_none" in _body.children[x].classList:
                    _body.children[x].classList.remove("display_none")

    def generate_head(self, _head=None, _data=None):
        # generate column title
        if not _head:
            _head = Famcy.thead()
        if not _data:
            _data = self.value["column"]

        self.column_dict = {}
        for t in _data:
            _tr = Famcy.tr()

            # generate btn
            if self.value["input_button"] and self.value["input_button"] != "none":
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
                self.column_dict[c["field"]] = c

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

        return _head

    def generate_body(self, _body=None, _data=None):
        # generate body info
        if not _body:
            _body = Famcy.tbody()
        if not _data:
            _data = self.value["data"]

        _body["id"] = "tbody"+self.id
        for i, d in enumerate(_data):
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

            for k in self.column_dict.keys():
                _td = Famcy.td()
                _td.style["text-align"] = self.column_dict[k]["align"]
                _td.style["vertical-align"] = self.column_dict[k]["valign"]
                _td["data-field"] = self.column_dict[k]["field"]
                _td.innerHTML = str(d[k]) if k in d.keys() else ""
                _tr.addElement(_td)

            _body.addElement(_tr)

        return _body

    def update_body_innerHTML(self):
        _body = self.body.children[1].children[1]
        _data = self.value["data"]

        for i, d in enumerate(_data):
            _tr = _body.children[i]

            for _i, k in enumerate(self.column_dict.keys()):
                _td = _tr.children[_i+self.radio_num]
                _td.innerHTML = str(d[k]) if k in d.keys() else ""
                
        return _body

    def find_table_element(self, row=None, col=None):
        self.update_body_innerHTML()
        return self.body.children[1].children[1].children[row].children[col+self.radio_num]

    def add_row(self, data):
        _add_row = [i for i in data if i not in self.value["data"]]

        # generate new table
        # =================================================
        self.value["data"] = data
        self.body.children[1].children[1] = self.generate_body(_body=self.body.children[1].children[1], _data=data)
        self.display_page(self.body.children[1].children[1], self.value["page_footer_detail"]["page_size"])
        # =================================================

        if isinstance(_add_row, list):
            _len = len(_add_row)
            _children = self.body.children[1].children[1].children
            target_element = []
            target_id = []
            target_parent = []
            for i in range(len(_children)-_len, len(_children)):
                t = _children[i]
                if isinstance(t, Famcy.FamcyElement):
                    target_element.append(t.render_inner())
                    target_id.append(t["id"])
                    target_parent.append(t.parentElement["id"])
            Famcy.sse.publish({"indicator": True, "message": {"target_parent": target_parent, "target_id": target_id, "target_element": target_element, "target_attribute": {}}}, type='publish', channel='event_source.table_'+self.id)

        else:
            print("Fail to add new row")

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

        _script = Famcy.script()
        _script.innerHTML = '''
        var source = new EventSource("/event_source?channel=event_source.table_%s");
        source.addEventListener('publish', function(event) {
            var data = JSON.parse(event.data);
            update_event_source_target(data)
        }, false);
        source.addEventListener('error', function(event) {
            console.log("Error"+ event)
        }, false);
        ''' % self.id
        self.body.addStaticScript(_script)

    def render_inner(self):
        # remove previous data
        self.body.children[1].children = []
        self.body.children[2].children = []

        self.generate_table()
        return self.body