from re_common.baselibrary.tools.myparsel import MParsel

if __name__ == '__main__':
    htmlText = r'''
    <body>
        <div class="book">111</div>
        <div class="journal_name">222</div>
        <div class="title">333</div>
        <a class ="link">link1</a>
        <a class ="link">link2</a>
        <a class ="link">link3</a>
    </body>
'''
    mc = MParsel()
    css_selector = {
        'book':'div[class="book"]::text',
        'journal_name':'div[class="journal_name"]::text',
        'title':'div[class="title"]::text',
        'link' :'a[class*="link"]::text'

    }
    xpath_selector = {
        'book': "//div[@class='book']/text()",
    }
    bools,new_dict = mc.css_parsel_html(htmlText,css_selector=css_selector)
    print(new_dict)
    bools, new_dict = mc.xpath_parsel_html(htmlText, xpath_selector=xpath_selector)
    print(new_dict)