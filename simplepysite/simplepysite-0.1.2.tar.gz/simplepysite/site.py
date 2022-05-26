import markdown as md
from glob import glob
import os

def establish_site():
    print("No directory 'pages' found.")
    print("Making a directory and sample page...")
    os.mkdir("pages")
    with open("pages//index.md",'w') as f:
        f.write(get_sample_md())
    with open("style.css",'w') as f:
        f.write(get_sample_css())
    print("Done.")

def build_site():
    print("Converting your site...")
    files_to_convert = glob(r"pages/*.md")
    for mdfile in files_to_convert:
        # text_from_file = get_text_from_file(mdfile)
        try:
            new_name = os.path.basename(mdfile)
            new_name = new_name[:-3] + ".html"
            md.markdownFromFile(input=mdfile, output=new_name, extensions=['tables','attr_list','wikilinks'])
        except Exception as e:
            print(f"Failed on page -{mdfile}- ; Exception was: {e}")

def get_sample_md():
    md_str = """# My page in simplepysite!

This is a super-simple static site generator. It is basically just some convenience functions built on top of the markdown library (required). This package will provide you with a very simple template for writing blog-like posts, as well as some simple css. Standard markdown syntax applies, and this is true for images and links.

## Why do this?

Many reasons!

1. I want to make lists like this one.
2. I don't like static site generators
3. While I like Markdeep its kind of tricky
4. I want to learn css

Here is some code I like!

```
print("Hello")
```

## Anything else?

No

### Really?

Correct

#### OK.

Goodbye

<footer>
Rocco Panella <br>
May 7 2022
</footer>

<link rel="stylesheet" href="style.css">"""
    return md_str

def get_sample_css():
    css_str = """body {
    font-family: Verdana, sans-serif;
    margin: auto;
    padding: 20px;
    max-width: 720px;
    text-align: left;
    background-color: #fff;
    word-wrap: break-word;
    overflow-wrap: break-word;
    line-height: 1.5;
    color: rgb(0, 0, 0)
}

h1,
h2,
h3,
h4,
h5,
h6,
strong,
b {
    color: #222
}

h1 {
    text-align: center;
    color: black
}


nav a {
    margin-right: 10px
}

textarea {
    width: 100%;
    font-size: 16px
}

input {
    font-size: 16px
}

content {
    line-height: 1.6
}

table {
    width: 100%
}

img {
    max-width: 100%
}

code {
    padding: 2px 5px;
    background-color: #f2f2f2
}

pre code {
    color: #222;
    display: block;
    padding: 20px;
    white-space: pre-wrap;
    font-size: 14px
}

div.highlight pre {
    background-color: initial;
    color: initial
}

div.highlight code {
    background-color: unset;
    color: unset
}

blockquote {
    border-left: 1px solid #999;
    color: #222;
    padding-left: 20px;
    font-style: italic
}

footer {
    padding: 25px;
    text-align: center
}

.helptext {
    color: #777;
    font-size: small
}

/* table, */
tbody,
tr,
td,
th {
    font-size: 12px;
    border: 2px solid black;
    padding: 2px;
  }

th {
    font-size: 8px;
}

  .center {
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 75%;
  }"""
    return css_str
