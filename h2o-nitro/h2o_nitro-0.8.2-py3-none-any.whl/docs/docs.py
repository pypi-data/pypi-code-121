# Copyright 2022 H2O.ai, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import os
from pathlib import Path
from h2o_nitro import web_directory, View, box, option, header, row, col, ContextSwitchError, lorem, Theme, \
    __version__ as version
import simple_websocket
from flask import Flask, request, send_from_directory
from werkzeug.utils import secure_filename


hello_world_docs = (
"""
## Basics - Hello World!
Call `view()` to show something on a page.
```py
view('Hello World!')
```
Here, `view()` is comparable to Python's built-in `print()` function,
and prints its arguments to the web page.
""",
    '### Output',
)


def hello_world(view: View):
    view_output(view, hello_world_docs, 'Hello World!')


format_content_docs = (
"""
## Basics - Formatting content
Strings passed to `view()` are interpreted as
[Markdown](https://github.github.com/gfm/)
```py
view('_Less_ `code` means _less_ **bugs**.')
```
""",
    '### Output',
)


def format_content(view: View):
    view_output(view, format_content_docs, '_Less_ `code` means _less_ **bugs**.')


format_multiline_content_docs = (
"""
## Basics - Show multiline content
Triple-quote strings to pass multiple lines of markdown.
```py
view('''
The King said, very gravely:
- Begin at the beginning,
- And go on till you come to the end,
- Then stop.
''')
```
""",
    '### Output',
)


def format_multiline_content(view: View):
    view_output(view, format_multiline_content_docs, '''
    The King said, very gravely:
    - Begin at the beginning,
    - And go on till you come to the end,
    - Then stop.
    ''')


display_multiple_docs = (
"""
## Basics - Show multiple items
Pass multiple arguments to `view()` to lay them out top to bottom.
```py
view(
    'Begin at the beginning,',
    'And go on till you come to the end,',
    'Then stop.',
)
```
""",
    '### Output',
)


def display_multiple(view: View):
    view_output(view, display_multiple_docs, 
        'Begin at the beginning,',
        'And go on till you come to the end,',
        'Then stop.',
    )


sequence_views_docs = (
"""
## Basics - Show multiple items, one at a time
Call `view()` multiple times to show items one at a time.

The following example steps through three different pages.
```py
view('Begin at the beginning,')
view('And go on till you come to the end,')
view('Then stop.')
```
""",
    '### Output',
)


def sequence_views(view: View):
    view_output(view, sequence_views_docs, 'Begin at the beginning,')
    view_output(view, sequence_views_docs, 'And go on till you come to the end,')
    view_output(view, sequence_views_docs, 'Then stop.')


style_text_docs = (
"""
## Basics - Style text
To style text, put it in a `box()`, and style the box.

`view(text)` is in fact shorthand for `view(box(text))`.
```py
view(
    box('Hello World!', color='red', border='red'),
    box('Hello World!', color='white', background='red'),
    box('Hello World!', width='50%', background='#eee'),
)
```
In general, `box()` can be used to create all kinds of content, like text blocks, dropdowns,
spinboxes, checklists, buttons, calendars, and so on.
""",
    '### Output',
)


def style_text(view: View):
    view_output(view, style_text_docs, 
        box('Hello World!', color='red', border='red'),
        box('Hello World!', color='white', background='red'),
        box('Hello World!', width='50%', background='#eee'),
    )


get_input_docs = (
"""
## Basics - Get user input
Call `box()` with `value=` to create an input field and pass it to `view()`.

When a view contains an input field, the `view()` function returns its input value.
```py
# Display a textbox and assign the entered value to a variable.
name = view(box('What is your name?', value='Boaty McBoatface'))
# Print the entered value.
view(f'Hello, {name}!')
```
Here, `view(box())` behaves similar to Python's built-in `input()` function.
""",
    '### Output',
)


def get_input(view: View):
    # Display a textbox and assign the entered value to a variable.
    name = view_output(view, get_input_docs, box('What is your name?', value='Boaty McBoatface'))
    # Print the entered value.
    view_output(view, get_input_docs, f'Hello, {name}!')


sequence_inputs_docs = (
"""
## Basics - Get multiple inputs, one at a time
Call `view()` multiple times to prompt for a sequence of inputs, one at a time.

The following example steps through three different pages.
```py
# Prompt for first name.
first_name = view(box('First name', value='Boaty'))
# Prompt for last name.
last_name = view(box('Last name', value='McBoatface'))
# Print the entered values.
view(f'Hello, {first_name} {last_name}!')
```
""",
    '### Output',
)


def sequence_inputs(view: View):
    # Prompt for first name.
    first_name = view_output(view, sequence_inputs_docs, box('First name', value='Boaty'))
    # Prompt for last name.
    last_name = view_output(view, sequence_inputs_docs, box('Last name', value='McBoatface'))
    # Print the entered values.
    view_output(view, sequence_inputs_docs, f'Hello, {first_name} {last_name}!')


accept_multiple_inputs_docs = (
"""
## Basics - Get multiple inputs at once
Pass multiple boxes to `view()` to prompt for inputs at once.

When a view contains multiple boxes, the `view()` function returns multiple values, in order.
```py
# Prompt for first and last names.
first_name, last_name = view(
    box('First name', value='Boaty'),
    box('Last name', value='McBoatface'),
)
# Print the entered values
view(f'Hello, {first_name} {last_name}!')
```
""",
    '### Output',
)


def accept_multiple_inputs(view: View):
    # Prompt for first and last names.
    first_name, last_name = view_output(view, accept_multiple_inputs_docs, 
        box('First name', value='Boaty'),
        box('Last name', value='McBoatface'),
    )
    # Print the entered values
    view_output(view, accept_multiple_inputs_docs, f'Hello, {first_name} {last_name}!')


dunk_your_donuts_docs = (
"""
## Basics - Putting it all together
Views can be chained together to create sophisticated workflows and wizards.

The example below shows a simple online ordering system.

Observe how it combines `view()` with conditionals and loops, while keeping the code
simple, concise, and clear.

Notably, if you have built web applications before, notice the absence of callbacks, event handlers,
web request handlers, routing, etc.
```py
# Our menu.
menu = dict(
    Donut=['Plain', 'Glazed', 'Chocolate'],
    Coffee=['Dark-roast', 'Medium-roast', 'Decaf'],
)

# Prompt for items.
items = view(box(
    'What would you like to order today?',
    options=list(menu.keys()),  # Menu item names.
    multiple=True,  # Allow multiple selections.
))

if len(items) == 0:  # Nothing selected.
    view(f'Nothing to order? Goodbye!')
    return

# The order summary, which we'll display later.
summary = ['### Order summary:']

# Prompt for counts and flavors.
for item in items:
    count = view(box(f'How many orders of {item} would you like?', value=3))
    for i in range(count):
        flavor = view(box(
            f'Pick a flavor for {item} #{i + 1}',
            options=menu[item],
        ))
        summary.append(f'1. {flavor} {item}')

summary.append('\\nThank you for your order!')

# Finally, show summary.
view('\\n'.join(summary))
```
Building a similar multi-page interactive app with a regular web framework can be
a fairly complex endeavor, weaving together requests and replies with logic spread across
multiple functions , but Nitro makes all this delightfully simple!
""",
    '### Output',
)


def dunk_your_donuts(view: View):
    # Our menu.
    menu = dict(
        Donut=['Plain', 'Glazed', 'Chocolate'],
        Coffee=['Dark-roast', 'Medium-roast', 'Decaf'],
    )

    # Prompt for items.
    items = view_output(view, dunk_your_donuts_docs, box(
        'What would you like to order today?',
        options=list(menu.keys()),  # Menu item names.
        multiple=True,  # Allow multiple selections.
    ))

    if len(items) == 0:  # Nothing selected.
        view_output(view, dunk_your_donuts_docs, f'Nothing to order? Goodbye!')
        return

    # The order summary, which we'll display later.
    summary = ['### Order summary:']

    # Prompt for counts and flavors.
    for item in items:
        count = view_output(view, dunk_your_donuts_docs, box(f'How many orders of {item} would you like?', value=3))
        for i in range(count):
            flavor = view_output(view, dunk_your_donuts_docs, box(
                f'Pick a flavor for {item} #{i + 1}',
                options=menu[item],
            ))
            summary.append(f'1. {flavor} {item}')

    summary.append('\nThank you for your order!')

    # Finally, show summary.
    view_output(view, dunk_your_donuts_docs, '\n'.join(summary))


markdown_basic_docs = (
"""
## Markdown - Basics
Strings passed to `view()` are interpreted as [Github Flavored Markdown](https://github.github.com/gfm/) (GFM).

`view(text)` is shorthand for `view(box(text))`.
```py
view('''
# Heading 1
## Heading 2
### Heading 3 
#### Heading 4
##### Heading 5 
###### Heading 6

This is a paragraph, with **bold**, *italics* 
(or _italics_), ***important***, `code`
and ~~strikethrough~~ formatting.

Here's a [hyperlink](https://example.com) to https://example.com.

![An image](https://picsum.photos/200)

> This is a block quote.

- List item 1
- List item 2
  - Sublist item 1
  - Sublist item 2
- List item 3

1. Numbered list item 1
1. Numbered list item 2
  1. Sublist item 1
  1. Sublist item 2
1. Numbered list item 3

Here is a footnote[^1] and another one[^another].

[^1]: A reference.
[^another]: Another reference.
''')
```
Any uniform indentation is automatically ignored.
""",
    '### Output',
)


def markdown_basic(view: View):
    view_output(view, markdown_basic_docs, '''
    # Heading 1
    ## Heading 2
    ### Heading 3 
    #### Heading 4
    ##### Heading 5 
    ###### Heading 6

    This is a paragraph, with **bold**, *italics* 
    (or _italics_), ***important***, `code`
    and ~~strikethrough~~ formatting.

    Here's a [hyperlink](https://example.com) to https://example.com.

    ![An image](https://picsum.photos/200)

    > This is a block quote.

    - List item 1
    - List item 2
      - Sublist item 1
      - Sublist item 2
    - List item 3

    1. Numbered list item 1
    1. Numbered list item 2
      1. Sublist item 1
      1. Sublist item 2
    1. Numbered list item 3

    Here is a footnote[^1] and another one[^another].

    [^1]: A reference.
    [^another]: Another reference.
    ''')


markdown_links_docs = (
"""
## Markdown - Handle clicks on links
Local links in markdown content behave just like any other input.

Clicking on a local link returns the name of the link.
```py
choice = view('''
Pick a flavor:
- [Vanilla](#vanilla)
- [Strawberry](#strawberry)
- [Chocolate](#chocolate)

Or, [surprise me](#surprise-me)!
''')
view(f'You clicked on {choice}.')
```
""",
    '### Output',
)


def markdown_links(view: View):
    choice = view_output(view, markdown_links_docs, '''
    Pick a flavor:
    - [Vanilla](#vanilla)
    - [Strawberry](#strawberry)
    - [Chocolate](#chocolate)

    Or, [surprise me](#surprise-me)!
    ''')
    view_output(view, markdown_links_docs, f'You clicked on {choice}.')


markdown_table_docs = (
"""
## Markdown - Show tables
Draw tables using `---` and `|`.

- Use three or more hyphens (`---`) to create each column’s header.
- Use `|` to separate each column.
- Use `:---` to left-align text.
- Use `:---:` to center text.
- Use `---:` to right-align text.
```py
view('''

### Basic Tables

| Flavor         | Super cheap! |
| -------------- | ------------ |
| Cinnamon Sugar | $1.99        |
| Powdered Sugar | $1.99        |
| Vanilla        | $2.99        |
| Chocolate      | $2.99        |
| Blueberry      | $2.99        |

### Column alignment

| Flavor         | Super cheap! | Extras                |
| -------------: | :----------: | :-------------------- |
| Cinnamon Sugar | $1.99        | Sugar and spice.      |
| Powdered Sugar | $1.99        | Served warm.          |
| Vanilla        | $2.99        | With cookie crumbles. |
| Chocolate      | $2.99        | With sprinkles.       |
| Blueberry      | $2.99        | With real blueberry.  |

''')
```
""",
    '### Output',
)


def markdown_table(view: View):
    view_output(view, markdown_table_docs, '''
    
    ### Basic Tables
    
    | Flavor         | Super cheap! |
    | -------------- | ------------ |
    | Cinnamon Sugar | $1.99        |
    | Powdered Sugar | $1.99        |
    | Vanilla        | $2.99        |
    | Chocolate      | $2.99        |
    | Blueberry      | $2.99        |
    
    ### Column alignment
    
    | Flavor         | Super cheap! | Extras                |
    | -------------: | :----------: | :-------------------- |
    | Cinnamon Sugar | $1.99        | Sugar and spice.      |
    | Powdered Sugar | $1.99        | Served warm.          |
    | Vanilla        | $2.99        | With cookie crumbles. |
    | Chocolate      | $2.99        | With sprinkles.       |
    | Blueberry      | $2.99        | With real blueberry.  |
    
    ''')


show_table_docs = (
"""
## Markdown - Create tables from lists
It's often easier to construct tables from lists of things, as shown below.
```py
def show_table(view: View):
    view(make_table([
        ['Flavor', 'Super cheap!'],
        ['Cinnamon Sugar', '$1.99'],
        ['Powdered Sugar', '$1.99'],
        ['Vanilla', '$2.99'],
        ['Chocolate', '$2.99'],
        ['Blueberry', '$2.99'],
    ]))


def make_table_row(row):
    return f"| {' | '.join(row)} |"


def make_table(rows):
    rows = [rows[0], ['---'] * len(rows[0]), *rows[1:]]
    return '\\n'.join([make_table_row(row) for row in rows])
```
""",
    '### Output',
)


def show_table(view: View):
    view_output(view, show_table_docs, make_table([
        ['Flavor', 'Super cheap!'],
        ['Cinnamon Sugar', '$1.99'],
        ['Powdered Sugar', '$1.99'],
        ['Vanilla', '$2.99'],
        ['Chocolate', '$2.99'],
        ['Blueberry', '$2.99'],
    ]))


def make_table_row(row):
    return f"| {' | '.join(row)} |"


def make_table(rows):
    rows = [rows[0], ['---'] * len(rows[0]), *rows[1:]]
    return '\n'.join([make_table_row(row) for row in rows])


markdown_syntax_highlighting_docs = (
"""
## Markdown - Syntax highlighting in code blocks
Code blocks in Markdown support syntax highlighting for 180+ languages using [highlight.js](https://highlightjs.org/).

To enable syntax highlighting, suffix the language to the opening triple-backticks.

[See list of supported languages](https://github.com/highlightjs/highlight.js/blob/main/SUPPORTED_LANGUAGES.md).
```py
view('''
Python:
```py
def hello():
    print('Hello!')
```

Ruby:
```rb
def hello
    puts "Hello!"
end
```

Javascript:
```js
function hello() {
    console.log('Hello!');
}
```
''')
```
""",
    '### Output',
)


def markdown_syntax_highlighting(view: View):
    view_output(view, markdown_syntax_highlighting_docs, '''
    Python:
    ```py
    def hello():
        print('Hello!')
    ```
    
    Ruby:
    ```rb
    def hello
        puts "Hello!"
    end
    ```

    Javascript:
    ```js
    function hello() {
        console.log('Hello!');
    }
    ```
    ''')


styling_background_docs = (
"""
## Styling - Set background color
Set `background=` to apply a background color.

The text color is automatically changed to a contrasting color if not specified.
A padding is automatically applied if not specified.
```py
text = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
do eiusmod tempor incididunt ut labore et dolore magna aliqua.
'''
view(
    box(text, background='#e63946'),
    box(text, background='#f1faee'),
    box(text, background='#a8dadc'),
    box(text, background='#457b9d'),
    box(text, background='#1d3557'),
)
```
""",
    '### Output',
)


def styling_background(view: View):
    text = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
    do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    '''
    view_output(view, styling_background_docs, 
        box(text, background='#e63946'),
        box(text, background='#f1faee'),
        box(text, background='#a8dadc'),
        box(text, background='#457b9d'),
        box(text, background='#1d3557'),
    )


styling_color_docs = (
"""
## Styling - Set text color
Set `color=` to change the text color.
```py
text = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
do eiusmod tempor incididunt ut labore et dolore magna aliqua.
'''
view(
    box(text, color='#e63946'),
    box(text, color='#457b9d'),
    box(text, color='#1d3557'),
)
```
""",
    '### Output',
)


def styling_color(view: View):
    text = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
    do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    '''
    view_output(view, styling_color_docs, 
        box(text, color='#e63946'),
        box(text, color='#457b9d'),
        box(text, color='#1d3557'),
    )


styling_border_docs = (
"""
## Styling - Set border color
Set `border=` to add a border.

A padding is automatically applied if not specified.
```py
text = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
do eiusmod tempor incididunt ut labore et dolore magna aliqua.
'''
view(
    box(text, border='#e63946'),
    box(text, border='#457b9d'),
    box(text, border='#1d3557'),
)
```
""",
    '### Output',
)


def styling_border(view: View):
    text = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
    do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    '''
    view_output(view, styling_border_docs, 
        box(text, border='#e63946'),
        box(text, border='#457b9d'),
        box(text, border='#1d3557'),
    )


styling_align_docs = (
"""
## Styling - Set text alignment
Set `align=` to `left`, `right`, `center` or `justify` to align text.
```py
text = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
'''
view(
    row(
        box(text, align='left'),
        box(text, align='center'),
        box(text, align='justify'),
        box(text, align='right'),
        gap=20,
    )
)
```
""",
    '### Output',
)


def styling_align(view: View):
    text = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    '''
    view_output(view, styling_align_docs, 
        row(
            box(text, align='left'),
            box(text, align='center'),
            box(text, align='justify'),
            box(text, align='right'),
            gap=20,
        )
    )


styling_size_docs = (
"""
## Styling - Set width and height
Nitro provides extensive control over how items are sized and spaced, using `width`, `height`, `margin`, `padding`,
and `gap`.

These parameters can be specified as either integers or strings.

- Integers are interpreted as pixels, e.g. `42` and `'42px'` have the same effect.
- Strings must be a number followed by one of the units listed below (e.g. `'42px'`, `'42in'`, `'42mm'`, etc.
- Absolute units:
- `px`: One pixel (1/96th of an inch).
- `cm`: One centimeter.
- `mm`: One millimeter.
- `in`: One inch (96px).
- `pc`: One pica (12pt or 1/6th of an inch).
- `pt`: One point (1/72nd of an inch).
- Relative units:
- `%`: A percentage of the container's size.
- `vh`: 1% of the viewport height.
- `vw`: 1% of the viewport width.
- `vmin`: The smaller of `vw` and `vh`.
- `vmax`: The larger of `vw` and `vh`.
- `ex`: The x-height of the font of the element.
- `em`: The font size of the element.
- `rem`: The font size of the page.
```py
text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
view(
    box(text, width=200, background='#eee'),  # interpreted as '200px'
    box(text, width='250px', background='#eee'),
    box(text, width='3in', background='#eee'),
    box(text, width='50%', background='#eee'),
    box(text, height='1in', background='#eee'),
    box(text, width='250px', height='100px', background='#eee'),
)
```
""",
    '### Output',
)


def styling_size(view: View):
    text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
    view_output(view, styling_size_docs, 
        box(text, width=200, background='#eee'),  # interpreted as '200px'
        box(text, width='250px', background='#eee'),
        box(text, width='3in', background='#eee'),
        box(text, width='50%', background='#eee'),
        box(text, height='1in', background='#eee'),
        box(text, width='250px', height='100px', background='#eee'),
    )


styling_margin_docs = (
"""
## Styling - Set margins
Set `margin=` to add a margin around each item.

Top, right, bottom, left margins can be controlled independently, and are specified
as `'top right bottom left'` strings.

- `'x'` is shorthand for `'x x x x'`.
- `'x y'` is shorthand for `'x y x y'`.
- `'x y z'` is shorthand for `'x y z y'`.
```py
text = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
do eiusmod tempor incididunt ut labore et dolore magna aliqua.
'''
boxes = [
    # Uniform 20px margin
    box(text, margin='20px', background='#eee'),
    # Same as '20px'
    box(text, margin=20, background='#eee'),
    # 0px top and bottom, 100px right and left margin
    box(text, margin='0px 100px', background='#eee'),
    # 0px top, 100px right and left, 30px bottom margin
    box(text, margin='0px 100px 30px', background='#eee'),
    # 0px top, 100px right, 30px bottom, 200px left margin
    box(text, margin='0px 100px 30px 200px', background='#eee'),
]
view(col(*[row(b, border='#000', padding=0) for b in boxes]))
```
""",
    '### Output',
)


def styling_margin(view: View):
    text = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
    do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    '''
    boxes = [
        # Uniform 20px margin
        box(text, margin='20px', background='#eee'),
        # Same as '20px'
        box(text, margin=20, background='#eee'),
        # 0px top and bottom, 100px right and left margin
        box(text, margin='0px 100px', background='#eee'),
        # 0px top, 100px right and left, 30px bottom margin
        box(text, margin='0px 100px 30px', background='#eee'),
        # 0px top, 100px right, 30px bottom, 200px left margin
        box(text, margin='0px 100px 30px 200px', background='#eee'),
    ]
    view_output(view, styling_margin_docs, col(*[row(b, border='#000', padding=0) for b in boxes]))


styling_padding_docs = (
"""
## Styling - Set padding
Set `padding=` to control the padding (inset) inside each item.

Top, right, bottom, left paddings can be controlled independently, and are specified
as `'top right bottom left'` strings.

- `'x'` is shorthand for `'x x x x'`.
- `'x y'` is shorthand for `'x y x y'`.
- `'x y z'` is shorthand for `'x y z y'`.
```py
text = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
do eiusmod tempor incididunt ut labore et dolore magna aliqua.
'''
view(
    col(
        # Uniform 20px padding
        box(text, padding='20px', background='#eee'),
        # Same as '20px'
        box(text, padding=20, background='#eee'),
        # 0px top and bottom, 100px right and left padding
        box(text, padding='0px 100px', background='#eee'),
        # 0px top, 100px right and left, 30px bottom padding
        box(text, padding='0px 100px 30px', background='#eee'),
        # 0px top, 100px right, 30px bottom, 200px left padding
        box(text, padding='0px 100px 30px 200px', background='#eee'),
    )
)
```
""",
    '### Output',
)


def styling_padding(view: View):
    text = '''
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed 
    do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    '''
    view_output(view, styling_padding_docs, 
        col(
            # Uniform 20px padding
            box(text, padding='20px', background='#eee'),
            # Same as '20px'
            box(text, padding=20, background='#eee'),
            # 0px top and bottom, 100px right and left padding
            box(text, padding='0px 100px', background='#eee'),
            # 0px top, 100px right and left, 30px bottom padding
            box(text, padding='0px 100px 30px', background='#eee'),
            # 0px top, 100px right, 30px bottom, 200px left padding
            box(text, padding='0px 100px 30px 200px', background='#eee'),
        )
    )


image_basic_docs = (
"""
## Images - Basic
Set `image=` to display an image.
```py
view(box(image='sample.jpg'))
```
Photo by [Ju Guan](https://unsplash.com/@guanju223?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText).
""",
    '### Output',
)


def image_basic(view: View):
    view_output(view, image_basic_docs, box(image='sample.jpg'))


image_resize_docs = (
"""
## Images - Set width and height
Images can be resized by setting `width=` or `height=` or both.

- If only `width=` or only `height=` are set, the image is scaled proportionally.
- If both `width=`and`height=`are set, the image is stretched to fit, and might appear distorted.
```py
view(
    box(image='sample.jpg', width=300),
    box(image='sample.jpg', height=200),
    box(image='sample.jpg', width=150, height=300),
)
```
""",
    '### Output',
)


def image_resize(view: View):
    view_output(view, image_resize_docs, 
        box(image='sample.jpg', width=300),
        box(image='sample.jpg', height=200),
        box(image='sample.jpg', width=150, height=300),
    )


image_fit_docs = (
"""
## Images - Scale and clip images
Set `fit=` to control how the image should be resized to fit its box.

- `fit='cover'` (default) scales and *clips* the image while preserving its aspect ratio.
- `fit='contain'` scales and *letterboxes* the image while preserving its aspect ratio.
- `fit='fill'` stretches the image to fit.
- `fit='none'` clips the image without resizing.
- `fit='scale-down'` behaves like either `contain` or `none`, whichever results in a smaller image.
```py
style = dict(width=100, height=200)
view(
    row(
        box(image='sample.jpg', fit='cover', **style),
        box(image='sample.jpg', fit='contain', **style),
        box(image='sample.jpg', fit='fill', **style),
        box(image='sample.jpg', fit='none', **style),
        box(image='sample.jpg', fit='scale-down', **style),
    )
)
```
""",
    '### Output',
)


def image_fit(view: View):
    style = dict(width=100, height=200)
    view_output(view, image_fit_docs, 
        row(
            box(image='sample.jpg', fit='cover', **style),
            box(image='sample.jpg', fit='contain', **style),
            box(image='sample.jpg', fit='fill', **style),
            box(image='sample.jpg', fit='none', **style),
            box(image='sample.jpg', fit='scale-down', **style),
        )
    )


image_background_docs = (
"""
## Images - Use as background
If a box contains content, its image is used as a background.

Set `fit=` to control how the background should be resized to fit the box.
```py
style = dict(width=100, height=200, color='white')
view(
    row(
        box('Astro', image='sample.jpg', **style),
        box('Astro', image='sample.jpg', fit='cover', **style),
        box('Astro', image='sample.jpg', fit='contain', **style),
        box('Astro', image='sample.jpg', fit='fill', **style),
        box('Astro', image='sample.jpg', fit='none', **style),
        image='sample.jpg',  # A background for the row as well!
    )
)
```
""",
    '### Output',
)


def image_background(view: View):
    style = dict(width=100, height=200, color='white')
    view_output(view, image_background_docs, 
        row(
            box('Astro', image='sample.jpg', **style),
            box('Astro', image='sample.jpg', fit='cover', **style),
            box('Astro', image='sample.jpg', fit='contain', **style),
            box('Astro', image='sample.jpg', fit='fill', **style),
            box('Astro', image='sample.jpg', fit='none', **style),
            image='sample.jpg',  # A background for the row as well!
        )
    )


image_background_pattern_docs = (
"""
## Images - Use as pattern
`image=` can also be set to a [Data URI](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs)
with a [base64-encoded](https://en.wikipedia.org/wiki/Base64) image.

The example below uses `fit='none'` to repeat a small PNG tile horizontally and vertically to form a pattern.
```py
view(box(
    '# Patterns!',
    image='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAEUlEQVQIHWNggIBiEGUFxJUABisBJ85jLc8AAAAASUVORK5CYII=',
    fit='none', height=300
))
```
""",
    '### Output',
)


def image_background_pattern(view: View):
    view_output(view, image_background_pattern_docs, box(
        '# Patterns!',
        image='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAEUlEQVQIHWNggIBiEGUFxJUABisBJ85jLc8AAAAASUVORK5CYII=',
        fit='none', height=300
    ))


layout_basic_docs = (
"""
## Layout - Basics
By default each item passed to `view()` are laid out one below the other, with a 10px gap.
```py
view(
    box(value='Top'),
    box(value='Middle'),
    box(value='Bottom'),
)
```
""",
    '### Output',
)


def layout_basic(view: View):
    view_output(view, layout_basic_docs, 
        box(value='Top'),
        box(value='Middle'),
        box(value='Bottom'),
    )


layout_row_docs = (
"""
## Layout - Lay out horizontally
Use `row()` to lay out multiple items horizontally, left to right.

By default, items take up equal amounts of space, with a `10px` gap between the items.
```py
view(row(
    box(value='Left'),
    box(value='Center'),
    box(value='Right'),
))
```
Setting `row=True` produces the same result as wrapping items with `row()`.
```py
view(
    box(value='Left'),
    box(value='Center'),
    box(value='Right'),
    row=True,
)
```
""",
    '### Output',
)


def layout_row(view: View):
    view_output(view, layout_row_docs, row(
        box(value='Left'),
        box(value='Center'),
        box(value='Right'),
    ))


def layout_row_alt(view: View):
    view_output(view, layout_row_docs, 
        box(value='Left'),
        box(value='Center'),
        box(value='Right'),
        row=True,
    )


layout_col_docs = (
"""
## Layout - Lay out vertically
Use `col()` to lay out multiple items vertically, top to bottom.

The example shows one row split into three columns containing three rows each.
```py
view(
    row(
        col(
            box(value='North-west'),
            box(value='West'),
            box(value='South-west'),
        ),
        col(
            box(value='North'),
            box(value='Center'),
            box(value='South'),
        ),
        col(
            box(value='North-east'),
            box(value='East'),
            box(value='South-east'),
        ),
    ),
)
```
""",
    '### Output',
)


def layout_col(view: View):
    view_output(view, layout_col_docs, 
        row(
            col(
                box(value='North-west'),
                box(value='West'),
                box(value='South-west'),
            ),
            col(
                box(value='North'),
                box(value='Center'),
                box(value='South'),
            ),
            col(
                box(value='North-east'),
                box(value='East'),
                box(value='South-east'),
            ),
        ),
    )


layout_tile_docs = (
"""
## Layout - Control tiling
Set `tile=` to control how items inside a view, row, or column are tiled along the main axis.

- The main axis for a row is horizontal, starting at the left, and ending at the right.
- The main axis for a column is vertical, starting at the top, and ending at the bottom

`tile=` can be set to `start`, `center`, `end`, `between`, `around`, `evenly`, `stretch`, or `normal`.
```py
boxes = [box(text=f'{i + 1}', background='#666', width=100) for i in range(3)]
row_style = dict(background='#eee')
view(
    # Pack items from the start.
    row(*boxes, tile='start', **row_style),

    # Pack items around the center.
    row(*boxes, tile='center', **row_style),

    # Pack items towards the end.
    row(*boxes, tile='end', **row_style),

    # Distribute items evenly.
    # The first item is flush with the start,
    # the last is flush with the end.
    row(*boxes, tile='between', **row_style),

    # Distribute items evenly.
    # Items have a half-size space on either side.
    row(*boxes, tile='around', **row_style),

    # Distribute items evenly.
    # Items have equal space around them.
    row(*boxes, tile='evenly', **row_style),

    # Default alignment.
    row(*boxes, tile='normal', **row_style),
)
```
""",
    '### Output',
)


def layout_tile(view: View):
    boxes = [box(text=f'{i + 1}', background='#666', width=100) for i in range(3)]
    row_style = dict(background='#eee')
    view_output(view, layout_tile_docs, 
        # Pack items from the start.
        row(*boxes, tile='start', **row_style),

        # Pack items around the center.
        row(*boxes, tile='center', **row_style),

        # Pack items towards the end.
        row(*boxes, tile='end', **row_style),

        # Distribute items evenly.
        # The first item is flush with the start,
        # the last is flush with the end.
        row(*boxes, tile='between', **row_style),

        # Distribute items evenly.
        # Items have a half-size space on either side.
        row(*boxes, tile='around', **row_style),

        # Distribute items evenly.
        # Items have equal space around them.
        row(*boxes, tile='evenly', **row_style),

        # Default alignment.
        row(*boxes, tile='normal', **row_style),
    )


layout_cross_tile_docs = (
"""
## Layout - Control cross tiling
Set `cross_tile=` to control how items inside a view, row, or column are tiled along the cross axis.

- The cross axis for a row is vertical. starting at the top, and ending at the bottom
- The cross axis for a column is horizontal, starting at the left, and ending at the right.

`cross_tile=` can be set to `start`, `center`, `end`, `stretch`, or `normal`.
```py
boxes = [box(text=f'{i + 1}', background='#666', width=100) for i in range(3)]
col_style = dict(height=200, background='#eee')
view(
    # Pack items from the start.
    col(row(*boxes, cross_tile='start'), **col_style),

    # Pack items around the center.
    col(row(*boxes, cross_tile='center'), **col_style),

    # Pack items towards the end.
    col(row(*boxes, cross_tile='end'), **col_style),

    # Stretch items to fit.
    col(row(*boxes, cross_tile='stretch'), **col_style),

    # Default alignment.
    col(row(*boxes, cross_tile='normal'), **col_style),
)
```
""",
    '### Output',
)


def layout_cross_tile(view: View):
    boxes = [box(text=f'{i + 1}', background='#666', width=100) for i in range(3)]
    col_style = dict(height=200, background='#eee')
    view_output(view, layout_cross_tile_docs, 
        # Pack items from the start.
        col(row(*boxes, cross_tile='start'), **col_style),

        # Pack items around the center.
        col(row(*boxes, cross_tile='center'), **col_style),

        # Pack items towards the end.
        col(row(*boxes, cross_tile='end'), **col_style),

        # Stretch items to fit.
        col(row(*boxes, cross_tile='stretch'), **col_style),

        # Default alignment.
        col(row(*boxes, cross_tile='normal'), **col_style),
    )


layout_gap_docs = (
"""
## Layout - Control spacing
Set `gap=` to control the spacing between items. The default gap is `10` or `'10px'`.
```py
view(
    box(value='Top'),
    box(value='Middle'),
    box(value='Bottom'),
    gap=25,
)
```
""",
    '### Output',
)


def layout_gap(view: View):
    view_output(view, layout_gap_docs, 
        box(value='Top'),
        box(value='Middle'),
        box(value='Bottom'),
        gap=25,
    )


layout_wrap_docs = (
"""
## Layout - Control wrapping
Set `wrap=` to control how items are wrapped inside a view, row, or column.

`wrap=` can be set to `start`, `center`, `end`, `between`, `around`, `evenly`, `stretch`, or `normal`.
```py
boxes = [box(text=f'{i + 1}', background='#666', width=150, height=50) for i in range(9)]
row_style = dict(height=300, background='#eee')
view(
    # Pack items from the start.
    row(*boxes, wrap='start', **row_style),

    # Pack items around the center.
    row(*boxes, wrap='center', **row_style),

    # Pack items towards the end.
    row(*boxes, wrap='end', **row_style),

    # Distribute items evenly.
    # The first item is flush with the start,
    # the last is flush with the end.
    row(*boxes, wrap='between', **row_style),

    # Distribute items evenly.
    # Items have a half-size space on either side.
    row(*boxes, wrap='around', **row_style),

    # Distribute items evenly.
    # Items have equal space around them.
    row(*boxes, wrap='evenly', **row_style),

    # Default alignment.
    row(*boxes, wrap='normal', **row_style),
)
```
""",
    '### Output',
)


def layout_wrap(view: View):
    boxes = [box(text=f'{i + 1}', background='#666', width=150, height=50) for i in range(9)]
    row_style = dict(height=300, background='#eee')
    view_output(view, layout_wrap_docs, 
        # Pack items from the start.
        row(*boxes, wrap='start', **row_style),

        # Pack items around the center.
        row(*boxes, wrap='center', **row_style),

        # Pack items towards the end.
        row(*boxes, wrap='end', **row_style),

        # Distribute items evenly.
        # The first item is flush with the start,
        # the last is flush with the end.
        row(*boxes, wrap='between', **row_style),

        # Distribute items evenly.
        # Items have a half-size space on either side.
        row(*boxes, wrap='around', **row_style),

        # Distribute items evenly.
        # Items have equal space around them.
        row(*boxes, wrap='evenly', **row_style),

        # Default alignment.
        row(*boxes, wrap='normal', **row_style),
    )


layout_grow_shrink_docs = (
"""
## Layout - Grow or shrink some items
Set `grow=` or `shrink=` to specify what amount of the available space the item should take up
inside a view, row, or column.

Setting `grow=` expands the item. Setting `shrink=` contracts the item. Both are proportions.

By default, items are grown or shrunk based on their initial size. To resize them on a different basis,
set `basis=` to the value you want.

- `basis=0` means "distribute available space assuming that the initial size is zero".
- `basis='20px'` means "distribute available space assuming that the initial size is 20px".
- The default behavior (if `basis=` is not set) is to assume that the initial size is the size of the item's content.
```py
box_style = dict(background='#666')
row_style = dict(background='#eee')
view(
    '1:?:?',
    row(
        # Take up all available space.
        box('a', grow=1, **box_style),
        box('b', width=50, **box_style),
        box('c', width=50, **box_style),
        **row_style,
    ),
    '1:1:?',
    row(
        # Take up one part of available space = 1 / (1 + 1).
        box('a', grow=1, **box_style),
        # Take up one part of available space = 1 / (1 + 1).
        box('b', grow=1, **box_style),
        box('c', width=50, **box_style),
        **row_style,
    ),
    '2:1:?',
    row(
        # Take up two parts of available space = 2 / (2 + 1).
        box('a', grow=2, **box_style),
        # Take up one part of available space = 1 / (2 + 1).
        box('b', grow=1, **box_style),
        box('c', width=50, **box_style),
        **row_style,
    ),
    '1:2:3:?',
    row(
        # Take up one part of available space = 1 / (1 + 2 + 3).
        box('a', grow=1, **box_style),
        # Take up two parts of available space = 2 / (1 + 2 + 3).
        box('b', grow=2, **box_style),
        # Take up three parts of available space = 3 / (1 + 2 + 3).
        box('c', grow=3, **box_style),
        box('d', width=50, **box_style),
        **row_style,
    ),
    '1:1:1:1',
    row(
        # Divide available space equally.
        box('a', grow=1, **box_style),
        box('b', grow=1, **box_style),
        box('c', grow=1, **box_style),
        box('d', grow=1, **box_style),
        **row_style,
    ),
)
```
""",
    '### Output',
)


def layout_grow_shrink(view: View):
    box_style = dict(background='#666')
    row_style = dict(background='#eee')
    view_output(view, layout_grow_shrink_docs, 
        '1:?:?',
        row(
            # Take up all available space.
            box('a', grow=1, **box_style),
            box('b', width=50, **box_style),
            box('c', width=50, **box_style),
            **row_style,
        ),
        '1:1:?',
        row(
            # Take up one part of available space = 1 / (1 + 1).
            box('a', grow=1, **box_style),
            # Take up one part of available space = 1 / (1 + 1).
            box('b', grow=1, **box_style),
            box('c', width=50, **box_style),
            **row_style,
        ),
        '2:1:?',
        row(
            # Take up two parts of available space = 2 / (2 + 1).
            box('a', grow=2, **box_style),
            # Take up one part of available space = 1 / (2 + 1).
            box('b', grow=1, **box_style),
            box('c', width=50, **box_style),
            **row_style,
        ),
        '1:2:3:?',
        row(
            # Take up one part of available space = 1 / (1 + 2 + 3).
            box('a', grow=1, **box_style),
            # Take up two parts of available space = 2 / (1 + 2 + 3).
            box('b', grow=2, **box_style),
            # Take up three parts of available space = 3 / (1 + 2 + 3).
            box('c', grow=3, **box_style),
            box('d', width=50, **box_style),
            **row_style,
        ),
        '1:1:1:1',
        row(
            # Divide available space equally.
            box('a', grow=1, **box_style),
            box('b', grow=1, **box_style),
            box('c', grow=1, **box_style),
            box('d', grow=1, **box_style),
            **row_style,
        ),
    )


layout_vertical_alignment_docs = (
"""
## Layout - Center content vertically
Use `tile='center'` to center content vertically inside a box.

The following example centers content both horizontally and vertically.
```py
view(
    box(
        '# Donuts',
        tile='center', cross_tile='center',
        height='300px', background='$foreground', color='$background',
    )
)
```
""",
    '### Output',
)


def layout_vertical_alignment(view: View):
    view_output(view, layout_vertical_alignment_docs, 
        box(
            '# Donuts',
            tile='center', cross_tile='center',
            height='300px', background='$foreground', color='$background',
        )
    )


form_basic_docs = (
"""
## Forms - Basic
To create a form, simply lay out all the inputs you need inside a view, then destructure the return value in order.
```py
username, password, action = view(
    box('Username', value='someone@company.com'),
    box('Password', value='pa55w0rd', password=True),
    box(['Login']),
)
view(f'You entered `{username}`/`{password}` and then clicked on {action}.')
```
""",
    '### Output',
)


def form_basic(view: View):
    username, password, action = view_output(view, form_basic_docs, 
        box('Username', value='someone@company.com'),
        box('Password', value='pa55w0rd', password=True),
        box(['Login']),
    )
    view_output(view, form_basic_docs, f'You entered `{username}`/`{password}` and then clicked on {action}.')


form_horizontal_docs = (
"""
## Forms - Horizontal
Wrap items with `row()` to lay them out left to right.
There is no change to the way the return values are destructured.
```py
username, password, action = view(
    row(
        box('Username', value='someone@company.com'),
        box('Password', value='pa55w0rd', password=True),
        box(['Login']),
    )
)
view(f'You entered `{username}`/`{password}` and then clicked on {action}.')
```
""",
    '### Output',
)


def form_horizontal(view: View):
    username, password, action = view_output(view, form_horizontal_docs, 
        row(
            box('Username', value='someone@company.com'),
            box('Password', value='pa55w0rd', password=True),
            box(['Login']),
        )
    )
    view_output(view, form_horizontal_docs, f'You entered `{username}`/`{password}` and then clicked on {action}.')


form_combo_docs = (
"""
## Forms - Combined
Use `row()` and `col()` to mix and match how items are laid out. Destructure the return values in the same order.
```py
first, last, addr1, addr2, city, state, zip, action = view(
    row(box('First name', value=''), box('Last name', value='')),
    box('Address line 1', value=''),
    box('Address line 2', value=''),
    row(box('City', value=''), box('State', value=''), box('Zip', value='')),
    box([
        option('yes', 'Sign me up!'),
        option('no', 'Not now'),
    ])
)
view(f'''
You provided:

Address: {first} {last}, {addr1}, {addr2}, {city} {state} {zip}

Sign up: {action}
''')
```
""",
    '### Output',
)


def form_combo(view: View):
    first, last, addr1, addr2, city, state, zip, action = view_output(view, form_combo_docs, 
        row(box('First name', value=''), box('Last name', value='')),
        box('Address line 1', value=''),
        box('Address line 2', value=''),
        row(box('City', value=''), box('State', value=''), box('Zip', value='')),
        box([
            option('yes', 'Sign me up!'),
            option('no', 'Not now'),
        ])
    )
    view_output(view, form_combo_docs, f'''
    You provided:
    
    Address: {first} {last}, {addr1}, {addr2}, {city} {state} {zip}
    
    Sign up: {action}
    ''')


form_improved_docs = (
"""
## Forms - Improved
Specify additional layout parameters like `width=`, `grow=`, etc. to get more control over
how items are laid out.
```py
first, middle, last, addr1, addr2, city, state, zip, action = view(
    row(box('First name', value=''), box('M.I.', value='', width='10%'), box('Last name', value='')),
    box('Address line 1', value=''),
    box('Address line 2', value=''),
    row(box('City', value='', grow=5), box('State', value='', width='20%'), box('Zip', value='', grow=1)),
    box([
        option('yes', 'Sign me up!', caption='Terms and conditions apply'),
        option('no', 'Not now', caption="I'll decide later"),
    ])
)
view(f'''
You provided:

Address: {first} {middle} {last}, {addr1}, {addr2}, {city} {state} {zip}

Sign up: {action}
''')
```
""",
    '### Output',
)


def form_improved(view: View):
    first, middle, last, addr1, addr2, city, state, zip, action = view_output(view, form_improved_docs, 
        row(box('First name', value=''), box('M.I.', value='', width='10%'), box('Last name', value='')),
        box('Address line 1', value=''),
        box('Address line 2', value=''),
        row(box('City', value='', grow=5), box('State', value='', width='20%'), box('Zip', value='', grow=1)),
        box([
            option('yes', 'Sign me up!', caption='Terms and conditions apply'),
            option('no', 'Not now', caption="I'll decide later"),
        ])
    )
    view_output(view, form_improved_docs, f'''
    You provided:

    Address: {first} {middle} {last}, {addr1}, {addr2}, {city} {state} {zip}

    Sign up: {action}
    ''')


popup_basic_docs = (
"""
## Popups - Basic
Call `view()` with `popup=True` to show the view on a popup window.
```py
view(box(['Show a popup']))
view('Wait! Call us now for free donuts!', popup=True)
```
""",
    '### Output',
)


def popup_basic(view: View):
    view_output(view, popup_basic_docs, box(['Show a popup']))
    view_output(view, popup_basic_docs, 'Wait! Call us now for free donuts!', popup=True)


popup_title_docs = (
"""
## Popups - Set popup title
Set `title=` to set a title for the popup window.
```py
view(box(['Show a popup']))
view('Call us now for free donuts!', title='Wait!', popup=True)
```
""",
    '### Output',
)


def popup_title(view: View):
    view_output(view, popup_title_docs, box(['Show a popup']))
    view_output(view, popup_title_docs, 'Call us now for free donuts!', title='Wait!', popup=True)


popup_buttons_docs = (
"""
## Popups - Customize buttons
If the popup's body contains a set of buttons, they're used as the popup's dismiss buttons. Common uses for such
buttons are to accept, cancel or close a popup.
```py
view(box(['Show a popup']))
response = view(
    box('Call us now for free donuts!'),
    box(dict(yes='Yes, now!', no='Maybe later')),
    title='Wait!', popup=True,
)
if response == 'yes':
    view('Your donuts are on the way!')
else:
    view('No donuts for you.')
```
""",
    '### Output',
)


def popup_buttons(view: View):
    view_output(view, popup_buttons_docs, box(['Show a popup']))
    response = view_output(view, popup_buttons_docs, 
        box('Call us now for free donuts!'),
        box(dict(yes='Yes, now!', no='Maybe later')),
        title='Wait!', popup=True,
    )
    if response == 'yes':
        view_output(view, popup_buttons_docs, 'Your donuts are on the way!')
    else:
        view_output(view, popup_buttons_docs, 'No donuts for you.')


textbox_basic_docs = (
"""
## Textbox - Basic
Call `box()` with `mode='text'` to show a textbox.

The return value is the text entered into the box.
```py
x = view(box(mode='text'))
view(f'You entered {x}.')
```
""",
    '### Output',
)


def textbox_basic(view: View):
    x = view_output(view, textbox_basic_docs, box(mode='text'))
    view_output(view, textbox_basic_docs, f'You entered {x}.')


textbox_value_docs = (
"""
## Textbox - Set initial value
Set `value=` to prefill the box with a value.

`mode='text'` can be elided if `value=` is set.
```py
speed = view(box(value='60 km/h'))
view(f'Your speed is {speed} km/h.')
```
""",
    '### Output',
)


def textbox_value(view: View):
    speed = view_output(view, textbox_value_docs, box(value='60 km/h'))
    view_output(view, textbox_value_docs, f'Your speed is {speed} km/h.')


textbox_label_docs = (
"""
## Textbox - Set a label
Any text passed to `box()` is used as a label.
```py
speed = view(box('Speed', value='60'))
view(f'Your speed is {speed} km/h.')
```
""",
    '### Output',
)


def textbox_label(view: View):
    speed = view_output(view, textbox_label_docs, box('Speed', value='60'))
    view_output(view, textbox_label_docs, f'Your speed is {speed} km/h.')


textbox_placeholder_docs = (
"""
## Textbox - Show placeholder text
Use `placeholder=` to show placeholder text inside the box.
```py
speed = view(box('Speed', placeholder='0 km/h'))
view(f'Your speed is {speed} km/h.')
```
""",
    '### Output',
)


def textbox_placeholder(view: View):
    speed = view_output(view, textbox_placeholder_docs, box('Speed', placeholder='0 km/h'))
    view_output(view, textbox_placeholder_docs, f'Your speed is {speed} km/h.')


textbox_required_docs = (
"""
## Textbox - Mark as required
Set `required=True` to indicate that input is required.
```py
speed = view(box('Speed (km/h)', required=True))
view(f'Your speed is {speed} km/h.')
```
""",
    '### Output',
)


def textbox_required(view: View):
    speed = view_output(view, textbox_required_docs, box('Speed (km/h)', required=True))
    view_output(view, textbox_required_docs, f'Your speed is {speed} km/h.')


textbox_mask_docs = (
"""
## Textbox - Control input format
Set `mask=` to specify an input mask. An input mask is used to format the text field
for the expected entry.

For example, to accept a phone number, use an input mask containing three sets of digits.
```py
phone = view(box('Phone', mask='(999) 999 - 9999'))
view(f'Your phone number is {phone}.')
```
To construct the input mask:

- Use `a` to indicate a letter.
- Use `9` to indicate a number.
- Use `*` to indicate a letter or number.
- Use a backslash to escape any character.
""",
    '### Output',
)


def textbox_mask(view: View):
    phone = view_output(view, textbox_mask_docs, box('Phone', mask='(999) 999 - 9999'))
    view_output(view, textbox_mask_docs, f'Your phone number is {phone}.')


textbox_icon_docs = (
"""
## Textbox - Show an icon
Set `icon=` to show an icon at the end of the box.
```py
phrase = view(box('Filter results containing:', icon='Filter'))
view(f'You set a filter on `{phrase}`.')
```
""",
    '### Output',
)


def textbox_icon(view: View):
    phrase = view_output(view, textbox_icon_docs, box('Filter results containing:', icon='Filter'))
    view_output(view, textbox_icon_docs, f'You set a filter on `{phrase}`.')


textbox_prefix_docs = (
"""
## Textbox - Set prefix text
Set `prefix=` to show a prefix at the start of the box.
```py
website = view(box('Website', prefix='https://', value='example.com'))
view(f'Your website is https://{website}.')
```
""",
    '### Output',
)


def textbox_prefix(view: View):
    website = view_output(view, textbox_prefix_docs, box('Website', prefix='https://', value='example.com'))
    view_output(view, textbox_prefix_docs, f'Your website is https://{website}.')


textbox_suffix_docs = (
"""
## Textbox - Set suffix text
Set `suffix=` to show a suffix at the end of the box.
```py
website = view(box('Website', suffix='.com', value='example'))
view(f'Your website is {website}.com.')
```
""",
    '### Output',
)


def textbox_suffix(view: View):
    website = view_output(view, textbox_suffix_docs, box('Website', suffix='.com', value='example'))
    view_output(view, textbox_suffix_docs, f'Your website is {website}.com.')


textbox_prefix_suffix_docs = (
"""
## Textbox - Set both prefix and suffix texts
A textbox can show both a prefix and a suffix at the same time.
```py
website = view(box('Website', prefix='https://', suffix='.com', value='example'))
view(f'Your website is https://{website}.com.')
```
""",
    '### Output',
)


def textbox_prefix_suffix(view: View):
    website = view_output(view, textbox_prefix_suffix_docs, box('Website', prefix='https://', suffix='.com', value='example'))
    view_output(view, textbox_prefix_suffix_docs, f'Your website is https://{website}.com.')


textbox_error_docs = (
"""
## Textbox - Show an error message
Set `error=` to show an error message below the box.
```py
speed = view(box('Speed (km/h)', error='Invalid input'))
```
""",
    '### Output',
)


def textbox_error(view: View):
    speed = view_output(view, textbox_error_docs, box('Speed (km/h)', error='Invalid input'))


textbox_password_docs = (
"""
## Textbox - Accept a password
Set `password=True` when accepting passwords and other confidential inputs.
```py
password = view(box('Password field', password=True))
view(f'Your password `{password}` is not strong enough!')
```
""",
    '### Output',
)


def textbox_password(view: View):
    password = view_output(view, textbox_password_docs, box('Password field', password=True))
    view_output(view, textbox_password_docs, f'Your password `{password}` is not strong enough!')


textarea_docs = (
"""
## Textbox - Enable multiple lines
Set `lines=` to show a multi-line text box (also called a *text area*).
```py
bio = view(box('Bio:', lines=5))
view(f'**Bio:** {bio}')
```
Note that `lines=` only controls the initial height of the textbox, and
multi-line textboxes can be resized by the user.
""",
    '### Output',
)


def textarea(view: View):
    bio = view_output(view, textarea_docs, box('Bio:', lines=5))
    view_output(view, textarea_docs, f'**Bio:** {bio}')


spinbox_basic_docs = (
"""
## Spinbox - Basic
Call `box()` with `mode='number'` to show a box with increment/decrement buttons.
(also called a *spinbox*).
```py
speed = view(box('Speed (km/h)', mode='number'))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def spinbox_basic(view: View):
    speed = view_output(view, spinbox_basic_docs, box('Speed (km/h)', mode='number'))
    view_output(view, spinbox_basic_docs, f'Your speed is {speed} km/h')


spinbox_value_docs = (
"""
## Spinbox - Set initial value
Set `value=` to a numeric value to prefill the box with the value.

The mode setting `mode='number'` is implied, and can be elided.
```py
speed = view(box('Speed (km/h)', value=42))
view(f'Your speed is {speed} km/h')
```
In other words, calling `box()` with a numeric `value` has the same effect
as setting `mode='number'`, and is the preferred usage.
""",
    '### Output',
)


def spinbox_value(view: View):
    speed = view_output(view, spinbox_value_docs, box('Speed (km/h)', value=42))
    view_output(view, spinbox_value_docs, f'Your speed is {speed} km/h')


spinbox_min_docs = (
"""
## Spinbox - Set min value
Set `min=` to specify a minimum value.
```py
speed = view(box('Speed (km/h)', min=10))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def spinbox_min(view: View):
    speed = view_output(view, spinbox_min_docs, box('Speed (km/h)', min=10))
    view_output(view, spinbox_min_docs, f'Your speed is {speed} km/h')


spinbox_max_docs = (
"""
## Spinbox - Set max value
Set `max=` to specify a maximum value.
```py
speed = view(box('Speed (km/h)', max=100))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def spinbox_max(view: View):
    speed = view_output(view, spinbox_max_docs, box('Speed (km/h)', max=100))
    view_output(view, spinbox_max_docs, f'Your speed is {speed} km/h')


spinbox_step_docs = (
"""
## Spinbox - Set step
Set `step=` to specify how much to increment or decrement by.

The default step is `1`.
```py
speed = view(box('Speed (km/h)', step=5))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def spinbox_step(view: View):
    speed = view_output(view, spinbox_step_docs, box('Speed (km/h)', step=5))
    view_output(view, spinbox_step_docs, f'Your speed is {speed} km/h')


spinbox_precision_docs = (
"""
## Spinbox - Set precision
Set `precision=` to specify how many decimal places the value should be rounded to.

The default is calculated based on the precision of step:

- if step = 1, precision = 0
- if step = 0.42, precision = 2
- if step = 0.0042, precision = 4
```py
speed = view(box('Speed (m/s)', value=0.6, min=-2, max=2, step=0.2, precision=2))
view(f'Your speed is {speed} m/s')
```
""",
    '### Output',
)


def spinbox_precision(view: View):
    speed = view_output(view, spinbox_precision_docs, box('Speed (m/s)', value=0.6, min=-2, max=2, step=0.2, precision=2))
    view_output(view, spinbox_precision_docs, f'Your speed is {speed} m/s')


spinbox_range_docs = (
"""
## Spinbox - Combine min, max, step, precision
`min=`, `max=`, `step=` and `precision=` can be combined.
```py
speed = view(box('Speed (km/h)', min=10, max=100, step=5))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def spinbox_range(view: View):
    speed = view_output(view, spinbox_range_docs, box('Speed (km/h)', min=10, max=100, step=5))
    view_output(view, spinbox_range_docs, f'Your speed is {speed} km/h')


spinbox_range_alt_docs = (
"""
## Spinbox - Set range
Set `range=` to a `(min, max)` tuple to restrict numeric inputs between two values.

This is a shorthand notation for setting `min=` and `max=` individually.
```py
speed = view(box('Speed (km/h)', range=(10, 100)))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def spinbox_range_alt(view: View):
    speed = view_output(view, spinbox_range_alt_docs, box('Speed (km/h)', range=(10, 100)))
    view_output(view, spinbox_range_alt_docs, f'Your speed is {speed} km/h')


spinbox_range_alt_step_docs = (
"""
## Spinbox - Set range with step
Set `range=` to a `(min, max, step)` tuple to increment/decrement by steps other than `1`.

This is a shorthand notation for setting `min=`, `max=` and `step` individually.
```py
speed = view(box('Speed (km/h)', range=(10, 100, 5)))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def spinbox_range_alt_step(view: View):
    speed = view_output(view, spinbox_range_alt_step_docs, box('Speed (km/h)', range=(10, 100, 5)))
    view_output(view, spinbox_range_alt_step_docs, f'Your speed is {speed} km/h')


spinbox_range_alt_precision_docs = (
"""
## Spinbox - Set range with precision
Setting `range=` to a `(min, max, step, precision)` tuple is a shorthand notation for setting
`min=`, `max=`, `step` and `precision` individually.
```py
speed = view(box('Speed (m/s)', value=0.6, range=(-2, 2, 0.2, 2)))
view(f'Your speed is {speed} m/s')
```
""",
    '### Output',
)


def spinbox_range_alt_precision(view: View):
    speed = view_output(view, spinbox_range_alt_precision_docs, box('Speed (m/s)', value=0.6, range=(-2, 2, 0.2, 2)))
    view_output(view, spinbox_range_alt_precision_docs, f'Your speed is {speed} m/s')


spinbox_negative_docs = (
"""
## Spinbox - Use zero-crossing ranges
Ranges can cross zero.
```py
speed = view(box('Speed (m/s)', value=-3, range=(-5, 5)))
view(f'Your speed is {speed} m/s')
```
""",
    '### Output',
)


def spinbox_negative(view: View):
    speed = view_output(view, spinbox_negative_docs, box('Speed (m/s)', value=-3, range=(-5, 5)))
    view_output(view, spinbox_negative_docs, f'Your speed is {speed} m/s')


spinbox_decimal_step_docs = (
"""
## Spinbox - Use fractional steps
Steps can be fractional.
```py
speed = view(box('Speed (m/s)', value=0.6, range=(-2, 2, 0.2)))
view(f'Your speed is {speed} m/s')
```
""",
    '### Output',
)


def spinbox_decimal_step(view: View):
    speed = view_output(view, spinbox_decimal_step_docs, box('Speed (m/s)', value=0.6, range=(-2, 2, 0.2)))
    view_output(view, spinbox_decimal_step_docs, f'Your speed is {speed} m/s')


checkbox_basic_docs = (
"""
## Checkbox - Basic
Set `mode='check'` to show a checkbox.
```py
keep_signed_in = view(box('Keep me signed in', mode='check'))
view(f'Keep me signed in: {keep_signed_in}.')
```
""",
    '### Output',
)


def checkbox_basic(view: View):
    keep_signed_in = view_output(view, checkbox_basic_docs, box('Keep me signed in', mode='check'))
    view_output(view, checkbox_basic_docs, f'Keep me signed in: {keep_signed_in}.')


checkbox_value_docs = (
"""
## Checkbox - Set initial value
Set `value=True` to pre-select the checkbox.

The mode setting `mode='check'` is implied, and can be elided.
```py
keep_signed_in = view(box('Keep me signed in', value=True))
view(f'Keep me signed in: {keep_signed_in}.')
```
""",
    '### Output',
)


def checkbox_value(view: View):
    keep_signed_in = view_output(view, checkbox_value_docs, box('Keep me signed in', value=True))
    view_output(view, checkbox_value_docs, f'Keep me signed in: {keep_signed_in}.')


toggle_basic_docs = (
"""
## Toggle - Basic
Set `mode='toggle'` to show a toggle.

A toggle represents a physical switch that allows someone to choose between two mutually exclusive options.
For example, “On/Off”, “Show/Hide”. Choosing an option should produce an immediate result.

Note that unlike a checkbox, a toggle returns its value immediately, much like a button.
This lets you handle the changed value immediately.
To keep the toggle displayed until the user is done, call `view()` inside a `while` loop.
```py
glazed, sprinkles, hot, done = True, False, False, False
while not done:
    glazed, sprinkles, hot, done = view(
        '### Customize my donut!',
        box('Make it glazed', mode='toggle', value=glazed),
        box('Add sprinkles', mode='toggle', value=sprinkles),
        box('Make it hot', mode='toggle', value=hot),
        box(['Place order'])
    )
view(f'''
You want your donut {"glazed" if glazed else "frosted"}, 
{"with" if sprinkles else "without"} sprinkles, 
and {"hot" if hot else "warm"}!
''')
```
""",
    '### Output',
)


def toggle_basic(view: View):
    glazed, sprinkles, hot, done = True, False, False, False
    while not done:
        glazed, sprinkles, hot, done = view_output(view, toggle_basic_docs, 
            '### Customize my donut!',
            box('Make it glazed', mode='toggle', value=glazed),
            box('Add sprinkles', mode='toggle', value=sprinkles),
            box('Make it hot', mode='toggle', value=hot),
            box(['Place order'])
        )
    view_output(view, toggle_basic_docs, f'''
    You want your donut {"glazed" if glazed else "frosted"}, 
    {"with" if sprinkles else "without"} sprinkles, 
    and {"hot" if hot else "warm"}!
    ''')


picker_basic_docs = (
"""
## Pickers - Basic
A *picker* is a box that allows the user to pick one or more options from several presented options, like buttons,
checklists, dropdowns, color pickers, and so on.

Set `options=` to create a picker.
```py
choice = view(box('Choose a color', options=[
    'green', 'yellow', 'orange', 'red'
]))
view(f'You chose {choice}.')
```
There are several ways to create options. These are explained in the next section. The simplest way is to supply a
sequence (tuple, set or list) of strings.

By default, this shows buttons for up to 3 options, radio buttons for up to 7 options,
or a dropdown menu for more than 7 options.
This behavior can be controlled using `mode=`, explained in later examples.

The example above has 4 options, hence radio buttons are shown.
""",
    '### Output',
)


def picker_basic(view: View):
    choice = view_output(view, picker_basic_docs, box('Choose a color', options=[
        'green', 'yellow', 'orange', 'red'
    ]))
    view_output(view, picker_basic_docs, f'You chose {choice}.')


picker_buttons_docs = (
"""
## Pickers - Show buttons
Buttons are shown for up to 3 options.

Set `mode='button'` to display buttons regardless of the number of options.
```py
choice = view(box('Choose a color', options=[
    'yellow', 'orange', 'red'
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def picker_buttons(view: View):
    choice = view_output(view, picker_buttons_docs, box('Choose a color', options=[
        'yellow', 'orange', 'red'
    ]))
    view_output(view, picker_buttons_docs, f'You chose {choice}.')


picker_radio_docs = (
"""
## Pickers - Show radio buttons
Radio buttons is shown for 4-7 options.

Set `mode='radio'` to display radio buttons regardless of the number of options.
```py
choice = view(box('Choose a color', options=[
    'green', 'yellow', 'orange', 'red'
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def picker_radio(view: View):
    choice = view_output(view, picker_radio_docs, box('Choose a color', options=[
        'green', 'yellow', 'orange', 'red'
    ]))
    view_output(view, picker_radio_docs, f'You chose {choice}.')


picker_dropdown_docs = (
"""
## Pickers - Show a dropdown menu
A dropdown menu is shown for more than 7 options.

Set `mode='menu'` to display a dropdown menu regardless of the number of options.
```py
choice = view(box('Choose a color', options=[
    'violet', 'indigo', 'blue', 'green', 'yellow', 'orange', 'red', 'black'
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def picker_dropdown(view: View):
    choice = view_output(view, picker_dropdown_docs, box('Choose a color', options=[
        'violet', 'indigo', 'blue', 'green', 'yellow', 'orange', 'red', 'black'
    ]))
    view_output(view, picker_dropdown_docs, f'You chose {choice}.')


picker_multiple_dropdown_docs = (
"""
## Pickers - Show a dropdown list
Set `multiple=True` to allow choosing more than one option. The return value is a list of choices made.

By default, this displays checkboxes for up to 7 options, or a dropdown menu for more than 7 options.

Set `mode='menu'` to display a dropdown menu regardless of the number of options.
```py
choices = view(box('Choose some colors', multiple=True, options=[
    'violet', 'indigo', 'blue', 'green', 'yellow', 'orange', 'red', 'black'
]))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def picker_multiple_dropdown(view: View):
    choices = view_output(view, picker_multiple_dropdown_docs, box('Choose some colors', multiple=True, options=[
        'violet', 'indigo', 'blue', 'green', 'yellow', 'orange', 'red', 'black'
    ]))
    view_output(view, picker_multiple_dropdown_docs, f'You chose {choices}.')


picker_checklist_docs = (
"""
## Pickers - Show a checklist
A checklist is shown for up to 7 options when `multiple=True`.

Set `mode='check'` to display a checklist regardless of the number of options.
```py
choices = view(box('Choose some colors', mode='check', multiple=True, options=[
    'yellow', 'orange', 'red', 'black'
]))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def picker_checklist(view: View):
    choices = view_output(view, picker_checklist_docs, box('Choose some colors', mode='check', multiple=True, options=[
        'yellow', 'orange', 'red', 'black'
    ]))
    view_output(view, picker_checklist_docs, f'You chose {choices}.')


picker_dropdown_required_docs = (
"""
## Pickers - Mark as required
Set `required=True` to indicate that input is required.
```py
choice = view(box('Choose a color', mode='menu', required=True, options=[
    'yellow', 'orange', 'red', 'black'
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def picker_dropdown_required(view: View):
    choice = view_output(view, picker_dropdown_required_docs, box('Choose a color', mode='menu', required=True, options=[
        'yellow', 'orange', 'red', 'black'
    ]))
    view_output(view, picker_dropdown_required_docs, f'You chose {choice}.')


picker_dropdown_error_docs = (
"""
## Pickers - Show an error message
Set `error=` to show an error message below the box.
```py
choice = view(box('Choose a color', mode='menu', error='Invalid input', options=[
    'yellow', 'orange', 'red', 'black'
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def picker_dropdown_error(view: View):
    choice = view_output(view, picker_dropdown_error_docs, box('Choose a color', mode='menu', error='Invalid input', options=[
        'yellow', 'orange', 'red', 'black'
    ]))
    view_output(view, picker_dropdown_error_docs, f'You chose {choice}.')


options_basic_docs = (
"""
## Options - Basic
An `option` represents one of several choices to be presented to the user.
It's used by all kinds of pickers: buttons, dropdowns, checklists, color pickers, and so on.

An option has a `value` and `text`, created using `option(value, text)`.

- The `value` is the value returned when the user picks that option. It is not user-visible.
- The `text` is typically used as a label for the option.

If `text` is not provided, then the `value` is also used as the `text`.

There are other, more concise ways to specify options, explained in later examples.
```py
choice = view(box('Choose a color', options=[
    option('green', 'Green'),
    option('yellow', 'Yellow'),
    option('orange', 'Orange'),
    option('red', 'Red'),
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def options_basic(view: View):
    choice = view_output(view, options_basic_docs, box('Choose a color', options=[
        option('green', 'Green'),
        option('yellow', 'Yellow'),
        option('orange', 'Orange'),
        option('red', 'Red'),
    ]))
    view_output(view, options_basic_docs, f'You chose {choice}.')


options_sequence_docs = (
"""
## Options - Create options from a sequence
If `options` is a sequence (tuple, set or list), the elements of the sequence are used as options.
```py
choice = view(box('Choose a color', options=[
    'green', 'yellow', 'orange', 'red'
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def options_sequence(view: View):
    choice = view_output(view, options_sequence_docs, box('Choose a color', options=[
        'green', 'yellow', 'orange', 'red'
    ]))
    view_output(view, options_sequence_docs, f'You chose {choice}.')


options_string_docs = (
"""
## Options - Create options from a string
If `options=` is set to a string, each word in the string is used as an option.
```py
choice = view(box('Choose a color', options='green yellow orange red'))
view(f'You chose {choice}.')
```
In other words, `'green yellow orange red'` is shorthand for `['green', 'yellow', 'orange', 'red']`.
""",
    '### Output',
)


def options_string(view: View):
    choice = view_output(view, options_string_docs, box('Choose a color', options='green yellow orange red'))
    view_output(view, options_string_docs, f'You chose {choice}.')


options_tuples_docs = (
"""
## Options - Create options from tuples
`options=` can also be specified as a sequence of `(value, text)` tuples.
```py
choice = view(box('Choose a color', options=[
    ('green', 'Green'),
    ('yellow', 'Yellow'),
    ('orange', 'Orange'),
    ('red', 'Red'),
]))
view(f'You chose {choice}.')
```
Here, `(value, text)` is shorthand for `option(value, text)`.
""",
    '### Output',
)


def options_tuples(view: View):
    choice = view_output(view, options_tuples_docs, box('Choose a color', options=[
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('orange', 'Orange'),
        ('red', 'Red'),
    ]))
    view_output(view, options_tuples_docs, f'You chose {choice}.')


options_dict_docs = (
"""
## Options - Create options from a dictionary
`options=` can also be specified as a `dict` of `value: text` entries.
```py
choice = view(box('Choose a color', options=dict(
    green='Green',
    yellow='Yellow',
    orange='Orange',
    red='Red',
)))
view(f'You chose {choice}.')
```
This is the most concise way to pass options where labels differ from values.
""",
    '### Output',
)


def options_dict(view: View):
    choice = view_output(view, options_dict_docs, box('Choose a color', options=dict(
        green='Green',
        yellow='Yellow',
        orange='Orange',
        red='Red',
    )))
    view_output(view, options_dict_docs, f'You chose {choice}.')


options_selected_docs = (
"""
## Options - Mark options as selected
Set `selected=True` to pre-select an option.

Another way to pre-select an option is to set `value=` on the box, as shown in the next example.
```py
choice = view(box('Choose a color', options=[
    option('green', 'Green'),
    option('yellow', 'Yellow', selected=True),
    option('orange', 'Orange'),
    option('red', 'Red'),
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def options_selected(view: View):
    choice = view_output(view, options_selected_docs, box('Choose a color', options=[
        option('green', 'Green'),
        option('yellow', 'Yellow', selected=True),
        option('orange', 'Orange'),
        option('red', 'Red'),
    ]))
    view_output(view, options_selected_docs, f'You chose {choice}.')


options_value_docs = (
"""
## Options - Set initial selection
Set `value=` on the box to pre-select an option having that value.

Another way to pre-select an option is to set `selected=True` on the option, as shown in the previous example.
```py
choice = view(box('Choose a color', value='yellow', options=[
    option('green', 'Green'),
    option('yellow', 'Yellow'),
    option('orange', 'Orange'),
    option('red', 'Red'),
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def options_value(view: View):
    choice = view_output(view, options_value_docs, box('Choose a color', value='yellow', options=[
        option('green', 'Green'),
        option('yellow', 'Yellow'),
        option('orange', 'Orange'),
        option('red', 'Red'),
    ]))
    view_output(view, options_value_docs, f'You chose {choice}.')


buttons_basic_docs = (
"""
## Buttons - Basic
Set `mode='button'` to show buttons.

`mode=` can be elided when there are 1-3 options.
```py
choice = view(box('Choose a color', mode='button', options=[
    'auto', 'yellow', 'orange', 'red',
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def buttons_basic(view: View):
    choice = view_output(view, buttons_basic_docs, box('Choose a color', mode='button', options=[
        'auto', 'yellow', 'orange', 'red',
    ]))
    view_output(view, buttons_basic_docs, f'You chose {choice}.')


buttons_shorthand_docs = (
"""
## Buttons - Shorthand notation
Most often, it doesn't make sense to show a text prompt above a set of buttons.

In such cases, `box(mode='button', options=X)` can be shortened to `box(X)`.

In other words, if the first argument to `box()` is a sequence of options, then `mode='button'` is implied.
```py
# Longer
choice = view(box(mode='button', options=['auto', 'yellow', 'orange', 'red']))

# Shorter
choice = view(box(['auto', 'yellow', 'orange', 'red']))

view(f'You chose {choice}.')
```
`options` can be a sequence of options, a sequence of tuples, or a dictionary. The following forms are equivalent:
```py
# Longer
choice = view(box([
    option('auto', 'Automatic'),
    option('yellow', 'Yellow'),
    option('orange', 'Orange'),
    option('red', 'Red'),
]))

# Shorter
choice = view(box([
    ('auto', 'Automatic'),
    ('yellow', 'Yellow'),
    ('orange', 'Orange'),
    ('red', 'Red'),
]))

# Shortest
choice = view(box(dict(
    auto='Automatic',
    yellow='Yellow',
    orange='Orange',
    red='Red',
)))
```
""",
    '### Output',
)


def buttons_shorthand(view: View):
    # Longer
    choice = view_output(view, buttons_shorthand_docs, box(mode='button', options=['auto', 'yellow', 'orange', 'red']))

    # Shorter
    choice = view_output(view, buttons_shorthand_docs, box(['auto', 'yellow', 'orange', 'red']))

    view_output(view, buttons_shorthand_docs, f'You chose {choice}.')


def buttons_shorthand_alt(view: View):
    # Longer
    choice = view_output(view, buttons_shorthand_docs, box([
        option('auto', 'Automatic'),
        option('yellow', 'Yellow'),
        option('orange', 'Orange'),
        option('red', 'Red'),
    ]))

    # Shorter
    choice = view_output(view, buttons_shorthand_docs, box([
        ('auto', 'Automatic'),
        ('yellow', 'Yellow'),
        ('orange', 'Orange'),
        ('red', 'Red'),
    ]))

    # Shortest
    choice = view_output(view, buttons_shorthand_docs, box(dict(
        auto='Automatic',
        yellow='Yellow',
        orange='Orange',
        red='Red',
    )))


buttons_selected_docs = (
"""
## Buttons - Mark button as primary
By default, the first button is displayed as the primary action in the sequence.

To select a different button as primary, set `selected=True`.
```py
choice = view(
    'Updates are available!',
    box([
        option('now', 'Update now'),
        option('tomorrow', 'Remind me tomorrow', selected=True),
        option('never', 'Never update'),
    ])
)
view(f'You chose to update {choice}.')
```
""",
    '### Output',
)


def buttons_selected(view: View):
    choice = view_output(view, buttons_selected_docs, 
        'Updates are available!',
        box([
            option('now', 'Update now'),
            option('tomorrow', 'Remind me tomorrow', selected=True),
            option('never', 'Never update'),
        ])
    )
    view_output(view, buttons_selected_docs, f'You chose to update {choice}.')


buttons_value_docs = (
"""
## Buttons - Select primary button
Alternatively, Set `value=` to mark a button as *primary*.
```py
choice = view(
    'Updates are available!',
    box(dict(
        now='Update now',
        tomorrow='Remind me tomorrow',
        never='Never update',
    ), value='now')
)
view(f'You chose to update {choice}.')
```
""",
    '### Output',
)


def buttons_value(view: View):
    choice = view_output(view, buttons_value_docs, 
        'Updates are available!',
        box(dict(
            now='Update now',
            tomorrow='Remind me tomorrow',
            never='Never update',
        ), value='now')
    )
    view_output(view, buttons_value_docs, f'You chose to update {choice}.')


buttons_values_docs = (
"""
## Buttons - Select multiple primary buttons
If `value=` is set to a sequence, all buttons with those values are marked as *primary*.
```py
choice = view(
    'Sign me up!',
    box(dict(
        basic='Basic Plan ($9.99/month)',
        pro='Pro Plan ($14.99/month)',
        none='Not interested',
    ), value=['basic', 'pro'])
)
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def buttons_values(view: View):
    choice = view_output(view, buttons_values_docs, 
        'Sign me up!',
        box(dict(
            basic='Basic Plan ($9.99/month)',
            pro='Pro Plan ($14.99/month)',
            none='Not interested',
        ), value=['basic', 'pro'])
    )
    view_output(view, buttons_values_docs, f'You chose {choice}.')


buttons_split_docs = (
"""
## Buttons - Add a menu
Sub-options inside options are shown as split buttons.
```py
choice = view(
    'Send fresh donuts every day?',
    box([
        option('yes', 'Yes!'),
        option('no', 'No', options=[
            option('later', 'Remind me later', icon='ChatBot'),
            option('never', "Don't ask me again", icon='MuteChat'),
        ]),
    ])
)
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def buttons_split(view: View):
    choice = view_output(view, buttons_split_docs, 
        'Send fresh donuts every day?',
        box([
            option('yes', 'Yes!'),
            option('no', 'No', options=[
                option('later', 'Remind me later', icon='ChatBot'),
                option('never', "Don't ask me again", icon='MuteChat'),
            ]),
        ])
    )
    view_output(view, buttons_split_docs, f'You chose {choice}.')


buttons_selected_split_docs = (
"""
## Buttons - Add a menu to a primary button
Sub-options work for primary buttons, too.
```py
choice = view(
    'Send fresh donuts every day?',
    box([
        option('yes', 'Yes!', options=[
            option('later', 'Remind me later', icon='ChatBot'),
            option('never', "Don't ask me again", icon='MuteChat'),
        ]),
        option('no', 'No'),
    ])
)
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def buttons_selected_split(view: View):
    choice = view_output(view, buttons_selected_split_docs, 
        'Send fresh donuts every day?',
        box([
            option('yes', 'Yes!', options=[
                option('later', 'Remind me later', icon='ChatBot'),
                option('never', "Don't ask me again", icon='MuteChat'),
            ]),
            option('no', 'No'),
        ])
    )
    view_output(view, buttons_selected_split_docs, f'You chose {choice}.')


buttons_caption_docs = (
"""
## Buttons - Set a caption
Set `caption=` to describe buttons.
```py
choice = view(
    'Send fresh donuts every day?',
    box([
        option('yes', 'Sign me up!', caption='Terms and conditions apply'),
        option('no', 'Not now', caption='I will decide later'),
    ])
)
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def buttons_caption(view: View):
    choice = view_output(view, buttons_caption_docs, 
        'Send fresh donuts every day?',
        box([
            option('yes', 'Sign me up!', caption='Terms and conditions apply'),
            option('no', 'Not now', caption='I will decide later'),
        ])
    )
    view_output(view, buttons_caption_docs, f'You chose {choice}.')


buttons_layout_docs = (
"""
## Buttons - Lay out buttons vertically
By default, buttons are arranged row-wise. Set `row=False` to arrange them column-wise.
```py
choice = view(
    'Choose a color:',
    box([
        option('auto', 'Automatic'),
        option('yellow', 'Yellow'),
        option('orange', 'Orange'),
        option('red', 'Red'),
    ], row=False)
)
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def buttons_layout(view: View):
    choice = view_output(view, buttons_layout_docs, 
        'Choose a color:',
        box([
            option('auto', 'Automatic'),
            option('yellow', 'Yellow'),
            option('orange', 'Orange'),
            option('red', 'Red'),
        ], row=False)
    )
    view_output(view, buttons_layout_docs, f'You chose {choice}.')


radio_basic_docs = (
"""
## Radio Buttons - Basic
Set `mode='radio'` to show radio buttons.

`mode=` can be elided when there are 4-7 options.

The first option is automatically selected.
```py
choice = view(box('Choose a color', mode='radio', options=[
    'blue', 'green', 'yellow', 'orange', 'red', 'black'
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def radio_basic(view: View):
    choice = view_output(view, radio_basic_docs, box('Choose a color', mode='radio', options=[
        'blue', 'green', 'yellow', 'orange', 'red', 'black'
    ]))
    view_output(view, radio_basic_docs, f'You chose {choice}.')


radio_value_docs = (
"""
## Radio Buttons - Set initial selection
Set `value=` to pre-select an option having that value.
```py
choice = view(box('Choose a color', mode='radio', value='yellow', options=[
    option('green', 'Green'),
    option('yellow', 'Yellow'),
    option('orange', 'Orange'),
    option('red', 'Red'),
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def radio_value(view: View):
    choice = view_output(view, radio_value_docs, box('Choose a color', mode='radio', value='yellow', options=[
        option('green', 'Green'),
        option('yellow', 'Yellow'),
        option('orange', 'Orange'),
        option('red', 'Red'),
    ]))
    view_output(view, radio_value_docs, f'You chose {choice}.')


radio_selected_docs = (
"""
## Radio Buttons - Mark options as selected
Set `selected=True` to pre-select an option.
```py
choice = view(box('Choose a color', mode='radio', options=[
    option('green', 'Green'),
    option('yellow', 'Yellow', selected=True),
    option('orange', 'Orange'),
    option('red', 'Red'),
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def radio_selected(view: View):
    choice = view_output(view, radio_selected_docs, box('Choose a color', mode='radio', options=[
        option('green', 'Green'),
        option('yellow', 'Yellow', selected=True),
        option('orange', 'Orange'),
        option('red', 'Red'),
    ]))
    view_output(view, radio_selected_docs, f'You chose {choice}.')


radio_icon_docs = (
"""
## Radio Buttons - Show pictorial options
Set `icon=` to show pictorial options.
```py
choice = view(box('Choose a chart type', mode='radio', options=[
    option('area', 'Area', icon='AreaChart', selected=True),
    option('bar', 'Bar', icon='BarChartHorizontal'),
    option('column', 'Column', icon='BarChartVertical'),
    option('line', 'Line', icon='LineChart'),
    option('scatter', 'Scatter', icon='ScatterChart'),
    option('donut', 'Donut', icon='DonutChart'),
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def radio_icon(view: View):
    choice = view_output(view, radio_icon_docs, box('Choose a chart type', mode='radio', options=[
        option('area', 'Area', icon='AreaChart', selected=True),
        option('bar', 'Bar', icon='BarChartHorizontal'),
        option('column', 'Column', icon='BarChartVertical'),
        option('line', 'Line', icon='LineChart'),
        option('scatter', 'Scatter', icon='ScatterChart'),
        option('donut', 'Donut', icon='DonutChart'),
    ]))
    view_output(view, radio_icon_docs, f'You chose {choice}.')


dropdown_basic_docs = (
"""
## Dropdown - Basic
Set `mode='menu'` to show a dropdown menu.

`mode=` can be elided when there are more than 7 options.
```py
choice = view(box('Choose a color', mode='menu', options=[
    'yellow', 'orange', 'red', 'black'
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def dropdown_basic(view: View):
    choice = view_output(view, dropdown_basic_docs, box('Choose a color', mode='menu', options=[
        'yellow', 'orange', 'red', 'black'
    ]))
    view_output(view, dropdown_basic_docs, f'You chose {choice}.')


dropdown_value_docs = (
"""
## Dropdown - Set initial selection
Set `value=` to pre-select an option having that value.
```py
choice = view(box('Choose a color', mode='menu', value='yellow', options=[
    option('green', 'Green'),
    option('yellow', 'Yellow'),
    option('orange', 'Orange'),
    option('red', 'Red'),
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def dropdown_value(view: View):
    choice = view_output(view, dropdown_value_docs, box('Choose a color', mode='menu', value='yellow', options=[
        option('green', 'Green'),
        option('yellow', 'Yellow'),
        option('orange', 'Orange'),
        option('red', 'Red'),
    ]))
    view_output(view, dropdown_value_docs, f'You chose {choice}.')


dropdown_selected_docs = (
"""
## Dropdown - Mark options as selected
Set `selected=True` to pre-select an option.
```py
choice = view(box('Choose a color', mode='menu', options=[
    option('green', 'Green'),
    option('yellow', 'Yellow', selected=True),
    option('orange', 'Orange'),
    option('red', 'Red'),
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def dropdown_selected(view: View):
    choice = view_output(view, dropdown_selected_docs, box('Choose a color', mode='menu', options=[
        option('green', 'Green'),
        option('yellow', 'Yellow', selected=True),
        option('orange', 'Orange'),
        option('red', 'Red'),
    ]))
    view_output(view, dropdown_selected_docs, f'You chose {choice}.')


dropdown_grouped_docs = (
"""
## Dropdown - Group options
Options can have sub-options. This is useful for grouping options into categories.

`mode=menu` is implied if options are grouped.
```py
choice = view(box('Choose a color', options=[
    option('primary', 'Primary Colors', options=[
        option('red', 'Red'),
        option('blue', 'Blue'),
        option('yellow', 'Yellow'),
    ]),
    option('secondary', 'Secondary Colors', options=[
        option('violet', 'Violet'),
        option('green', 'Green'),
        option('orange', 'Orange'),
    ]),
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def dropdown_grouped(view: View):
    choice = view_output(view, dropdown_grouped_docs, box('Choose a color', options=[
        option('primary', 'Primary Colors', options=[
            option('red', 'Red'),
            option('blue', 'Blue'),
            option('yellow', 'Yellow'),
        ]),
        option('secondary', 'Secondary Colors', options=[
            option('violet', 'Violet'),
            option('green', 'Green'),
            option('orange', 'Orange'),
        ]),
    ]))
    view_output(view, dropdown_grouped_docs, f'You chose {choice}.')


dropdown_editable_docs = (
"""
## Dropdown - Enable arbitrary input
Set `editable=True` to allow arbitrary input in addition to the presented options.

`mode=menu` is implied if `editable=True`.
```py
choice = view(box('Choose a color', editable=True, options=[
    'yellow', 'orange', 'red', 'black'
]))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def dropdown_editable(view: View):
    choice = view_output(view, dropdown_editable_docs, box('Choose a color', editable=True, options=[
        'yellow', 'orange', 'red', 'black'
    ]))
    view_output(view, dropdown_editable_docs, f'You chose {choice}.')


multi_dropdown_basic_docs = (
"""
## Dropdown List - Basic
Set `mode='menu'` with `multiple=True` to show a dropdown menu that allows multiple options to be selected.

`mode=` can be elided when there are more than 7 options.
```py
choices = view(box(
    'Choose some colors',
    mode='menu',
    multiple=True,
    options=['green', 'yellow', 'orange', 'red']
))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def multi_dropdown_basic(view: View):
    choices = view_output(view, multi_dropdown_basic_docs, box(
        'Choose some colors',
        mode='menu',
        multiple=True,
        options=['green', 'yellow', 'orange', 'red']
    ))
    view_output(view, multi_dropdown_basic_docs, f'You chose {choices}.')


multi_dropdown_value_docs = (
"""
## Dropdown List - Set initial selection
Set `value=` to pre-select options having those values.
```py
choices = view(box(
    'Choose some colors',
    mode='menu',
    multiple=True,
    value=['yellow', 'red'],
    options=['green', 'yellow', 'orange', 'red']
))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def multi_dropdown_value(view: View):
    choices = view_output(view, multi_dropdown_value_docs, box(
        'Choose some colors',
        mode='menu',
        multiple=True,
        value=['yellow', 'red'],
        options=['green', 'yellow', 'orange', 'red']
    ))
    view_output(view, multi_dropdown_value_docs, f'You chose {choices}.')


multi_dropdown_selected_docs = (
"""
## Dropdown List - Mark options as selected
Alternatively, set `selected=True` to pre-select one or more options.
```py
choices = view(box(
    'Choose some colors',
    mode='menu',
    multiple=True,
    options=[
        option('green', 'Green'),
        option('yellow', 'Yellow', selected=True),
        option('orange', 'Orange'),
        option('red', 'Red', selected=True),
    ]
))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def multi_dropdown_selected(view: View):
    choices = view_output(view, multi_dropdown_selected_docs, box(
        'Choose some colors',
        mode='menu',
        multiple=True,
        options=[
            option('green', 'Green'),
            option('yellow', 'Yellow', selected=True),
            option('orange', 'Orange'),
            option('red', 'Red', selected=True),
        ]
    ))
    view_output(view, multi_dropdown_selected_docs, f'You chose {choices}.')


checklist_basic_docs = (
"""
## Checklist - Basic
Set `mode='check'` to show a checklist

`mode=` can be elided when there are 1-7 options.
```py
choices = view(box(
    'Choose some colors',
    mode='check',
    options=['green', 'yellow', 'orange', 'red']
))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def checklist_basic(view: View):
    choices = view_output(view, checklist_basic_docs, box(
        'Choose some colors',
        mode='check',
        options=['green', 'yellow', 'orange', 'red']
    ))
    view_output(view, checklist_basic_docs, f'You chose {choices}.')


checklist_value_docs = (
"""
## Checklist - Set initial selection
Set `value=` to pre-select options having those values.
```py
choices = view(box(
    'Choose some colors',
    mode='check',
    value=['yellow', 'red'],
    options=['green', 'yellow', 'orange', 'red']
))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def checklist_value(view: View):
    choices = view_output(view, checklist_value_docs, box(
        'Choose some colors',
        mode='check',
        value=['yellow', 'red'],
        options=['green', 'yellow', 'orange', 'red']
    ))
    view_output(view, checklist_value_docs, f'You chose {choices}.')


checklist_selected_docs = (
"""
## Checklist - Mark options as checked
Alternatively, set `selected=True` to pre-select one or more options.
```py
choices = view(box(
    'Choose some colors',
    mode='check',
    options=[
        option('green', 'Green'),
        option('yellow', 'Yellow', selected=True),
        option('orange', 'Orange'),
        option('red', 'Red', selected=True),
    ]
))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def checklist_selected(view: View):
    choices = view_output(view, checklist_selected_docs, box(
        'Choose some colors',
        mode='check',
        options=[
            option('green', 'Green'),
            option('yellow', 'Yellow', selected=True),
            option('orange', 'Orange'),
            option('red', 'Red', selected=True),
        ]
    ))
    view_output(view, checklist_selected_docs, f'You chose {choices}.')


table_basic_docs = (
"""
## Table - Basic
Call `box()` with `mode='table'` to show a table.
```py
view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!'),
        header('Extras'),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
    ],
))
```
""",
    '### Output',
)


def table_basic(view: View):
    view_output(view, table_basic_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!'),
            header('Extras'),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ],
    ))


table_clickable_docs = (
"""
## Table - Make rows clickable
To make rows clickable, set `mode='link'` on a header.

If set, `view()` returns the `value` of the clicked row.
```py
choice = view(box(
    mode='table',
    headers=[
        header('Flavor', mode='link'),
        header('Super cheap!'),
        header('Extras'),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
    ],
))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def table_clickable(view: View):
    choice = view_output(view, table_clickable_docs, box(
        mode='table',
        headers=[
            header('Flavor', mode='link'),
            header('Super cheap!'),
            header('Extras'),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ],
    ))
    view_output(view, table_clickable_docs, f'You chose {choice}.')


table_markdown_docs = (
"""
## Table - Use markdown in cells
By default, cells are interpreted as plain text. To interpret them as markdown, set `mode='md'` on the header.
```py
choice = view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!'),
        header('Extras', mode='md'),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', '*Sugar and spice*']),
        option('sugar', options=['Powdered Sugar', '$1.99', '**Served warm**']),
        option('vanilla',
               options=['Vanilla', '$2.99', 'With [cookie](https://en.wikipedia.org/wiki/Cookie) crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With ~real~ blueberry']),
    ],
))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def table_markdown(view: View):
    choice = view_output(view, table_markdown_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!'),
            header('Extras', mode='md'),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', '*Sugar and spice*']),
            option('sugar', options=['Powdered Sugar', '$1.99', '**Served warm**']),
            option('vanilla',
                   options=['Vanilla', '$2.99', 'With [cookie](https://en.wikipedia.org/wiki/Cookie) crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With ~real~ blueberry']),
        ],
    ))
    view_output(view, table_markdown_docs, f'You chose {choice}.')


table_multiselect_docs = (
"""
## Table - Enable multi-select
Set `multiple=True` to allow rows to be selected. This effectively allow a table to be used in place of a
dropdown menu, especially useful when each item has multiple attributes.

The return value is a collection of the values of the selected rows.
```py
choices = view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!'),
        header('Extras'),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
    ],
    multiple=True,
))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def table_multiselect(view: View):
    choices = view_output(view, table_multiselect_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!'),
            header('Extras'),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ],
        multiple=True,
    ))
    view_output(view, table_multiselect_docs, f'You chose {choices}.')


table_singleselect_docs = (
"""
## Table - Enable single select
Set `multiple=False` to allow at most one row to be selected.

The return value is the `value` of the selected row.
```py
choice = view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!'),
        header('Extras'),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
    ],
    multiple=False,
))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def table_singleselect(view: View):
    choice = view_output(view, table_singleselect_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!'),
            header('Extras'),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ],
        multiple=False,
    ))
    view_output(view, table_singleselect_docs, f'You chose {choice}.')


table_value_docs = (
"""
## Table - Set initial selection
Set `value=` to pre-select one or more rows.
```py
choices = view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!'),
        header('Extras'),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
    ],
    multiple=True,
    value=['vanilla', 'blueberry'],
))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def table_value(view: View):
    choices = view_output(view, table_value_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!'),
            header('Extras'),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ],
        multiple=True,
        value=['vanilla', 'blueberry'],
    ))
    view_output(view, table_value_docs, f'You chose {choices}.')


table_selected_docs = (
"""
## Table - Mark rows as selected
Alternatively, set `selected=True` on a row to pre-select the row.
```py
choices = view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!'),
        header('Extras'),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles'], selected=True),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry'], selected=True),
    ],
    multiple=True,
))
view(f'You chose {choices}.')
```
""",
    '### Output',
)


def table_selected(view: View):
    choices = view_output(view, table_selected_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!'),
            header('Extras'),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles'], selected=True),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry'], selected=True),
        ],
        multiple=True,
    ))
    view_output(view, table_selected_docs, f'You chose {choices}.')


table_grouped_docs = (
"""
## Table - Group rows
To group rows, use nested options.
```py
choice = view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!'),
        header('Extras'),
    ],
    options=[
        option('donuts', text='Donuts', options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ]),
        option('coffee', text='Coffee', options=[
            option('blonde', options=['Blonde Roast', '$1.49', 'Light and creamy']),
            option('medium', options=['Medium Roast', '$1.49', 'House favorite']),
            option('dark', options=['Dark Roast', '$1.49', 'Bold and sassy']),
        ]),
    ],
))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def table_grouped(view: View):
    choice = view_output(view, table_grouped_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!'),
            header('Extras'),
        ],
        options=[
            option('donuts', text='Donuts', options=[
                option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
                option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
                option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
                option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
                option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
            ]),
            option('coffee', text='Coffee', options=[
                option('blonde', options=['Blonde Roast', '$1.49', 'Light and creamy']),
                option('medium', options=['Medium Roast', '$1.49', 'House favorite']),
                option('dark', options=['Dark Roast', '$1.49', 'Bold and sassy']),
            ]),
        ],
    ))
    view_output(view, table_grouped_docs, f'You chose {choice}.')


table_multilevel_docs = (
"""
## Table - Group rows at multiple levels
Rows can be nested at multiple levels.
```py
choice = view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!'),
        header('Extras'),
    ],
    options=[
        option('donuts', text='Donuts', options=[
            option('popular', text='Popular', options=[
                option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
                option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            ]),
            option('specialty', text='Specialty', options=[
                option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
                option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
                option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
            ]),
        ]),
        option('coffee', text='Coffee', options=[
            option('blonde', options=['Blonde Roast', '$1.49', 'Light and creamy']),
            option('medium', options=['Medium Roast', '$1.49', 'House favorite']),
            option('dark', options=['Dark Roast', '$1.49', 'Bold and sassy']),
        ]),
    ],
))
view(f'You chose {choice}.')
```
""",
    '### Output',
)


def table_multilevel(view: View):
    choice = view_output(view, table_multilevel_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!'),
            header('Extras'),
        ],
        options=[
            option('donuts', text='Donuts', options=[
                option('popular', text='Popular', options=[
                    option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
                    option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
                ]),
                option('specialty', text='Specialty', options=[
                    option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
                    option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
                    option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
                ]),
            ]),
            option('coffee', text='Coffee', options=[
                option('blonde', options=['Blonde Roast', '$1.49', 'Light and creamy']),
                option('medium', options=['Medium Roast', '$1.49', 'House favorite']),
                option('dark', options=['Dark Roast', '$1.49', 'Bold and sassy']),
            ]),
        ],
    ))
    view_output(view, table_multilevel_docs, f'You chose {choice}.')


table_column_width_docs = (
"""
## Table - Set column width
Set `width=` to set the minimum width of the column.

To set both minimum and maximum widths, set `width=` to a `(min, max)` tuple.
```py
view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!', width=100),
        header('Extras', width=(200, 300)),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
    ],
))
```
""",
    '### Output',
)


def table_column_width(view: View):
    view_output(view, table_column_width_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!', width=100),
            header('Extras', width=(200, 300)),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ],
    ))


table_header_icon_docs = (
"""
## Table - Set header icon
Set `icon=` to display an icon in the header instead of text.
```py
view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!', icon='Money'),
        header('Extras'),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
    ],
))
```
""",
    '### Output',
)


def table_header_icon(view: View):
    view_output(view, table_header_icon_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!', icon='Money'),
            header('Extras'),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ],
    ))


table_header_resizable_docs = (
"""
## Table - Disable column resizing
Set `resizable=False` to prevent a column from being resized.
```py
view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!', resizable=False),
        header('Extras'),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
    ],
))
```
""",
    '### Output',
)


def table_header_resizable(view: View):
    view_output(view, table_header_resizable_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!', resizable=False),
            header('Extras'),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ],
    ))


table_column_multiline_docs = (
"""
## Table - Enable multiline cells
Set `Multiline=True` to allow multiline text in a column's cells
```py
view(box(
    mode='table',
    headers=[
        header('Flavor'),
        header('Super cheap!'),
        header('Extras', multiline=True),
    ],
    options=[
        option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
        option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
        option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
        option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
        option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
    ],
))
```
""",
    '### Output',
)


def table_column_multiline(view: View):
    view_output(view, table_column_multiline_docs, box(
        mode='table',
        headers=[
            header('Flavor'),
            header('Super cheap!'),
            header('Extras', multiline=True),
        ],
        options=[
            option('cinnamon', options=['Cinnamon Sugar', '$1.99', 'Sugar and spice']),
            option('sugar', options=['Powdered Sugar', '$1.99', 'Served warm']),
            option('vanilla', options=['Vanilla', '$2.99', 'With cookie crumbles']),
            option('chocolate', options=['Chocolate', '$2.99', 'With sprinkles']),
            option('blueberry', options=['Blueberry', '$2.99', 'With real blueberry']),
        ],
    ))


slider_basic_docs = (
"""
## Slider - Basic
Set `mode='range'` to show a slider.

The default range is between `0` and `10`.
```py
speed = view(box('Speed (km/h)', mode='range'))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def slider_basic(view: View):
    speed = view_output(view, slider_basic_docs, box('Speed (km/h)', mode='range'))
    view_output(view, slider_basic_docs, f'Your speed is {speed} km/h')


slider_value_docs = (
"""
## Slider - Set initial value
Set `value=` to default the slider value.
```py
speed = view(box('Speed (km/h)', mode='range', value=5))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def slider_value(view: View):
    speed = view_output(view, slider_value_docs, box('Speed (km/h)', mode='range', value=5))
    view_output(view, slider_value_docs, f'Your speed is {speed} km/h')


slider_min_docs = (
"""
## Slider - Set min value
Set `min=` to specify a minimum value.
```py
speed = view(box('Speed (km/h)', mode='range', min=3))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def slider_min(view: View):
    speed = view_output(view, slider_min_docs, box('Speed (km/h)', mode='range', min=3))
    view_output(view, slider_min_docs, f'Your speed is {speed} km/h')


slider_max_docs = (
"""
## Slider - Set max value
Set `max=` to specify a maximum value.
```py
speed = view(box('Speed (km/h)', mode='range', max=100))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def slider_max(view: View):
    speed = view_output(view, slider_max_docs, box('Speed (km/h)', mode='range', max=100))
    view_output(view, slider_max_docs, f'Your speed is {speed} km/h')


slider_step_docs = (
"""
## Slider - Set step
Set `step=` to specify how much to increment or decrement by.

The default step is `1`.
```py
speed = view(box('Speed (km/h)', mode='range', step=2))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def slider_step(view: View):
    speed = view_output(view, slider_step_docs, box('Speed (km/h)', mode='range', step=2))
    view_output(view, slider_step_docs, f'Your speed is {speed} km/h')


slider_precision_docs = (
"""
## Slider - Set precision
Set `precision=` to specify how many decimal places the value should be rounded to.

The default is calculated based on the precision of step:

- if step = 1, precision = 0
- if step = 0.42, precision = 2
- if step = 0.0042, precision = 4
```py
speed = view(box('Speed (m/s)', mode='range', value=0.6, min=-2, max=2, step=0.2, precision=2))
view(f'Your speed is {speed} m/s')
```
""",
    '### Output',
)


def slider_precision(view: View):
    speed = view_output(view, slider_precision_docs, box('Speed (m/s)', mode='range', value=0.6, min=-2, max=2, step=0.2, precision=2))
    view_output(view, slider_precision_docs, f'Your speed is {speed} m/s')


slider_range_docs = (
"""
## Slider - Combine min, max, step, precision
`min=`, `max=`, `step=` and `precision=` can be combined.
```py
speed = view(box('Speed (km/h)', mode='range', min=10, max=100, step=5))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def slider_range(view: View):
    speed = view_output(view, slider_range_docs, box('Speed (km/h)', mode='range', min=10, max=100, step=5))
    view_output(view, slider_range_docs, f'Your speed is {speed} km/h')


slider_range_alt_docs = (
"""
## Slider - Set range
Set `range=` to a `(min, max)` tuple to restrict numeric inputs between two values.

This is a shorthand notation for setting `min=` and `max=` individually.
```py
speed = view(box('Speed (km/h)', mode='range', range=(10, 100)))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def slider_range_alt(view: View):
    speed = view_output(view, slider_range_alt_docs, box('Speed (km/h)', mode='range', range=(10, 100)))
    view_output(view, slider_range_alt_docs, f'Your speed is {speed} km/h')


slider_range_alt_step_docs = (
"""
## Slider - Set range with step
Set `range=` to a `(min, max, step)` tuple to increment/decrement by steps other than `1`.

This is a shorthand notation for setting `min=`, `max=` and `step` individually.
```py
speed = view(box('Speed (km/h)', mode='range', range=(10, 100, 5)))
view(f'Your speed is {speed} km/h')
```
""",
    '### Output',
)


def slider_range_alt_step(view: View):
    speed = view_output(view, slider_range_alt_step_docs, box('Speed (km/h)', mode='range', range=(10, 100, 5)))
    view_output(view, slider_range_alt_step_docs, f'Your speed is {speed} km/h')


slider_range_alt_precision_docs = (
"""
## Slider - Set range with precision
Setting `range=` to a `(min, max, step, precision)` tuple is shorthand setting
`min=`, `max=`, `step` and `precision` individually.
```py
speed = view(box('Speed (m/s)', mode='range', value=0.6, range=(-2, 2, 0.2, 2)))
view(f'Your speed is {speed} m/s')
```
""",
    '### Output',
)


def slider_range_alt_precision(view: View):
    speed = view_output(view, slider_range_alt_precision_docs, box('Speed (m/s)', mode='range', value=0.6, range=(-2, 2, 0.2, 2)))
    view_output(view, slider_range_alt_precision_docs, f'Your speed is {speed} m/s')


slider_negative_docs = (
"""
## Slider - Zero-crossing range
Ranges can cross zero.
```py
speed = view(box('Speed (m/s)', mode='range', value=-3, range=(-5, 5)))
view(f'Your speed is {speed} m/s')
```
""",
    '### Output',
)


def slider_negative(view: View):
    speed = view_output(view, slider_negative_docs, box('Speed (m/s)', mode='range', value=-3, range=(-5, 5)))
    view_output(view, slider_negative_docs, f'Your speed is {speed} m/s')


slider_decimal_step_docs = (
"""
## Slider - Set fractional steps
Steps can be fractional.
```py
speed = view(box('Speed (m/s)', mode='range', value=0.6, range=(-2, 2, 0.2)))
view(f'Your speed is {speed} m/s')
```
""",
    '### Output',
)


def slider_decimal_step(view: View):
    speed = view_output(view, slider_decimal_step_docs, box('Speed (m/s)', mode='range', value=0.6, range=(-2, 2, 0.2)))
    view_output(view, slider_decimal_step_docs, f'Your speed is {speed} m/s')


range_slider_basic_docs = (
"""
## Range Slider - Basic
Set `value=` to a `(start, end)` tuple to show a range slider.

The mode setting `mode='range'` is implied, and can be elided.
```py
start, end = view(box('Speed range (km/h)', value=(3, 7)))
view(f'Your speed ranges between {start} and {end} km/h')
```
""",
    '### Output',
)


def range_slider_basic(view: View):
    start, end = view_output(view, range_slider_basic_docs, box('Speed range (km/h)', value=(3, 7)))
    view_output(view, range_slider_basic_docs, f'Your speed ranges between {start} and {end} km/h')


range_slider_min_docs = (
"""
## Range Slider - Set min value
Set `min=` to specify a minimum value.
```py
start, end = view(box('Speed range (km/h)', value=(3, 7), min=3))
view(f'Your speed ranges between {start} and {end} km/h')
```
""",
    '### Output',
)


def range_slider_min(view: View):
    start, end = view_output(view, range_slider_min_docs, box('Speed range (km/h)', value=(3, 7), min=3))
    view_output(view, range_slider_min_docs, f'Your speed ranges between {start} and {end} km/h')


range_slider_max_docs = (
"""
## Range Slider - Set max value
Set `max=` to specify a maximum value.
```py
start, end = view(box('Speed range (km/h)', value=(30, 70), max=100))
view(f'Your speed ranges between {start} and {end} km/h')
```
""",
    '### Output',
)


def range_slider_max(view: View):
    start, end = view_output(view, range_slider_max_docs, box('Speed range (km/h)', value=(30, 70), max=100))
    view_output(view, range_slider_max_docs, f'Your speed ranges between {start} and {end} km/h')


range_slider_step_docs = (
"""
## Range Slider - Set step
Set `step=` to specify how much to increment or decrement by.

The default step is `1`.
```py
start, end = view(box('Speed range (km/h)', value=(2, 6), step=2))
view(f'Your speed ranges between {start} and {end} km/h')
```
""",
    '### Output',
)


def range_slider_step(view: View):
    start, end = view_output(view, range_slider_step_docs, box('Speed range (km/h)', value=(2, 6), step=2))
    view_output(view, range_slider_step_docs, f'Your speed ranges between {start} and {end} km/h')


range_slider_precision_docs = (
"""
## Range Slider - Set precision
Set `precision=` to specify how many decimal places the value should be rounded to.

The default is calculated based on the precision of step:
- if step = 1, precision = 0
- if step = 0.42, precision = 2
- if step = 0.0042, precision = 4
```py
start, end = view(box('Speed range (m/s)', value=(-0.4, 0.4), min=-2, max=2, step=0.2, precision=2))
view(f'Your speed ranges between {start} and {end} m/s')
```
""",
    '### Output',
)


def range_slider_precision(view: View):
    start, end = view_output(view, range_slider_precision_docs, box('Speed range (m/s)', value=(-0.4, 0.4), min=-2, max=2, step=0.2, precision=2))
    view_output(view, range_slider_precision_docs, f'Your speed ranges between {start} and {end} m/s')


range_slider_range_docs = (
"""
## Range Slider - Combine min, max, step, precision
`min=`, `max=`, `step=` and `precision=` can be combined.
```py
start, end = view(box('Speed range (km/h)', value=(30, 70), min=10, max=100, step=5))
view(f'Your speed ranges between {start} and {end} km/h')
```
""",
    '### Output',
)


def range_slider_range(view: View):
    start, end = view_output(view, range_slider_range_docs, box('Speed range (km/h)', value=(30, 70), min=10, max=100, step=5))
    view_output(view, range_slider_range_docs, f'Your speed ranges between {start} and {end} km/h')


range_slider_range_alt_docs = (
"""
## Range Slider - Set range
Set `range=` to a `(min, max)` tuple to restrict numeric inputs between two values.

This is a shorthand notation for setting `min=` and `max=` individually.
```py
start, end = view(box('Speed range (km/h)', value=(30, 70), range=(10, 100)))
view(f'Your speed ranges between {start} and {end} km/h')
```
""",
    '### Output',
)


def range_slider_range_alt(view: View):
    start, end = view_output(view, range_slider_range_alt_docs, box('Speed range (km/h)', value=(30, 70), range=(10, 100)))
    view_output(view, range_slider_range_alt_docs, f'Your speed ranges between {start} and {end} km/h')


range_slider_range_alt_step_docs = (
"""
## Range Slider - Set range with step
Set `range=` to a `(min, max, step)` tuple to increment/decrement by steps other than `1`.

This is a shorthand notation for setting `min=`, `max=` and `step` individually.
```py
start, end = view(box('Speed range (km/h)', value=(30, 70), range=(10, 100, 5)))
view(f'Your speed ranges between {start} and {end} km/h')
```
""",
    '### Output',
)


def range_slider_range_alt_step(view: View):
    start, end = view_output(view, range_slider_range_alt_step_docs, box('Speed range (km/h)', value=(30, 70), range=(10, 100, 5)))
    view_output(view, range_slider_range_alt_step_docs, f'Your speed ranges between {start} and {end} km/h')


range_slider_range_alt_precision_docs = (
"""
## Range Slider - Set range with precision
Set `range=` to a `(min, max, step)` tuple to increment/decrement by steps other than `1`.
Setting `range=` to a `(min, max, step, precision)` tuple is shorthand for setting
`min=`, `max=`, `step` and `precision` individually.
```py
start, end = view(box('Speed range (m/s)', value=(-0.4, 0.4), range=(-2, 2, 0.2, 2)))
view(f'Your speed ranges between {start} and {end} m/s')
```
""",
    '### Output',
)


def range_slider_range_alt_precision(view: View):
    start, end = view_output(view, range_slider_range_alt_precision_docs, box('Speed range (m/s)', value=(-0.4, 0.4), range=(-2, 2, 0.2, 2)))
    view_output(view, range_slider_range_alt_precision_docs, f'Your speed ranges between {start} and {end} m/s')


range_slider_negative_docs = (
"""
## Range Slider - Use zero-crossing range
Ranges can cross zero.
```py
start, end = view(box('Speed range (m/s)', value=(-3, 3), range=(-5, 5)))
view(f'Your speed ranges between {start} and {end} m/s')
```
""",
    '### Output',
)


def range_slider_negative(view: View):
    start, end = view_output(view, range_slider_negative_docs, box('Speed range (m/s)', value=(-3, 3), range=(-5, 5)))
    view_output(view, range_slider_negative_docs, f'Your speed ranges between {start} and {end} m/s')


range_slider_decimal_step_docs = (
"""
## Range Slider - Set fractional steps
Steps can be fractional.
```py
start, end = view(box('Speed range (m/s)', value=(-0.4, 0.4), range=(-2, 2, 0.2)))
view(f'Your speed ranges between {start} and {end} m/s')
```
""",
    '### Output',
)


def range_slider_decimal_step(view: View):
    start, end = view_output(view, range_slider_decimal_step_docs, box('Speed range (m/s)', value=(-0.4, 0.4), range=(-2, 2, 0.2)))
    view_output(view, range_slider_decimal_step_docs, f'Your speed ranges between {start} and {end} m/s')


time_basic_docs = (
"""
## Time Picker - Basic
Set `mode='time'` to show a time picker.
```py
time = view(box('Set alarm for:', mode='time', value='3:04PM'))
view(f'Alarm set for {time}.')
```
""",
    '### Output',
)


def time_basic(view: View):
    time = view_output(view, time_basic_docs, box('Set alarm for:', mode='time', value='3:04PM'))
    view_output(view, time_basic_docs, f'Alarm set for {time}.')


time_seconds_docs = (
"""
## Time Picker - Enable seconds
Include seconds in the `value` to show a seconds component.
```py
time = view(box('Set alarm for:', mode='time', value='3:04:05PM'))
view(f'Alarm set for {time}.')
```
""",
    '### Output',
)


def time_seconds(view: View):
    time = view_output(view, time_seconds_docs, box('Set alarm for:', mode='time', value='3:04:05PM'))
    view_output(view, time_seconds_docs, f'Alarm set for {time}.')


time_hour_docs = (
"""
## Time Picker - Show hours only
Exclude minutes and seconds from the `value` to show only the hour component.
```py
time = view(box('Set alarm for:', mode='time', value='3PM'))
view(f'Alarm set for {time}.')
```
""",
    '### Output',
)


def time_hour(view: View):
    time = view_output(view, time_hour_docs, box('Set alarm for:', mode='time', value='3PM'))
    view_output(view, time_hour_docs, f'Alarm set for {time}.')


time_24_docs = (
"""
## Time Picker - Show 24-hour clock
Exclude `AM` or `PM` from the `value` to accept input in military time.
```py
time = view(box('Set alarm for:', mode='time', value='15:04'))
view(f'Alarm set for {time}.')
```
""",
    '### Output',
)


def time_24(view: View):
    time = view_output(view, time_24_docs, box('Set alarm for:', mode='time', value='15:04'))
    view_output(view, time_24_docs, f'Alarm set for {time}.')


time_24_seconds_docs = (
"""
## Time Picker - Show 24-hour clock, with seconds
Include seconds in the `value` to show a seconds component.
```py
time = view(box('Set alarm for:', mode='time', value='15:04:05'))
view(f'Alarm set for {time}.')
```
""",
    '### Output',
)


def time_24_seconds(view: View):
    time = view_output(view, time_24_seconds_docs, box('Set alarm for:', mode='time', value='15:04:05'))
    view_output(view, time_24_seconds_docs, f'Alarm set for {time}.')


time_24_hour_docs = (
"""
## Time Picker - Show 24-hour clock, with hour only
Exclude minutes and seconds from the `value` to show only the hour component.
```py
time = view(box('Set alarm for:', mode='time', value='15'))
view(f'Alarm set for {time}.')
```
""",
    '### Output',
)


def time_24_hour(view: View):
    time = view_output(view, time_24_hour_docs, box('Set alarm for:', mode='time', value='15'))
    view_output(view, time_24_hour_docs, f'Alarm set for {time}.')


date_basic_docs = (
"""
## Date Picker - Basic
Set `mode='date'` to show a date-picker.
```py
date = view(box('Pick a date', mode='date'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def date_basic(view: View):
    date = view_output(view, date_basic_docs, box('Pick a date', mode='date'))
    view_output(view, date_basic_docs, f'You picked {date}.')


date_value_docs = (
"""
## Date Picker - Set initial date
Set `value=` to pre-select a date.

Dates must be in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format.
Date-only strings (e.g. "1970-01-01") are treated as UTC, not local.
```py
date = view(box('Pick a date', mode='date', value='2021-10-10'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def date_value(view: View):
    date = view_output(view, date_value_docs, box('Pick a date', mode='date', value='2021-10-10'))
    view_output(view, date_value_docs, f'You picked {date}.')


date_placeholder_docs = (
"""
## Date Picker - Set placeholder text
Set `placeholder=` to show placeholder text.
```py
date = view(box('Deliver on', mode='date', placeholder='Delivery date'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def date_placeholder(view: View):
    date = view_output(view, date_placeholder_docs, box('Deliver on', mode='date', placeholder='Delivery date'))
    view_output(view, date_placeholder_docs, f'You picked {date}.')


date_min_docs = (
"""
## Date Picker - Set min date
Set `min=` to specify a minimum date.
```py
date = view(box('Pick a date', mode='date', value='2021-10-10', min='2019-01-01'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def date_min(view: View):
    date = view_output(view, date_min_docs, box('Pick a date', mode='date', value='2021-10-10', min='2019-01-01'))
    view_output(view, date_min_docs, f'You picked {date}.')


date_max_docs = (
"""
## Date Picker - Set max date
Set `max=` to specify a maximum date.
```py
date = view(box('Pick a date', mode='date', value='2021-10-10', max='2022-12-31'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def date_max(view: View):
    date = view_output(view, date_max_docs, box('Pick a date', mode='date', value='2021-10-10', max='2022-12-31'))
    view_output(view, date_max_docs, f'You picked {date}.')


date_min_max_docs = (
"""
## Date Picker - Combine min and max date
Set both `min=` and `max=` to restrict selection between two dates.
```py
date = view(box('Pick a date', mode='date', value='2021-10-10', min='2019-01-01', max='2022-12-31'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def date_min_max(view: View):
    date = view_output(view, date_min_max_docs, box('Pick a date', mode='date', value='2021-10-10', min='2019-01-01', max='2022-12-31'))
    view_output(view, date_min_max_docs, f'You picked {date}.')


date_range_docs = (
"""
## Date Picker - Set range
Set `range=` to a `(min, max)` tuple to restrict selection between two dates.

This is a shorthand notation for setting `min=` and `max=` individually.
```py
date = view(box('Pick a date', mode='date', value='2021-10-10', range=('2019-01-01', '2022-12-31')))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def date_range(view: View):
    date = view_output(view, date_range_docs, box('Pick a date', mode='date', value='2021-10-10', range=('2019-01-01', '2022-12-31')))
    view_output(view, date_range_docs, f'You picked {date}.')


date_required_docs = (
"""
## Date Picker - Mark as required
Set `required=True` to indicate that input is required.
```py
date = view(box('Pick a date', mode='date', required=True))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def date_required(view: View):
    date = view_output(view, date_required_docs, box('Pick a date', mode='date', required=True))
    view_output(view, date_required_docs, f'You picked {date}.')


day_basic_docs = (
"""
## Calendar - Basic
Set `mode='day'` to show a calendar.
```py
date = view(box('Pick a date', mode='day'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def day_basic(view: View):
    date = view_output(view, day_basic_docs, box('Pick a date', mode='day'))
    view_output(view, day_basic_docs, f'You picked {date}.')


day_value_docs = (
"""
## Calendar - Set initial date
Set `value=` to pre-select a date.

Dates must be in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format.
Date-only strings (e.g. "1970-01-01") are treated as UTC, not local.
```py
date = view(box('Pick a date', mode='day', value='2021-10-10'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def day_value(view: View):
    date = view_output(view, day_value_docs, box('Pick a date', mode='day', value='2021-10-10'))
    view_output(view, day_value_docs, f'You picked {date}.')


day_min_docs = (
"""
## Calendar - Set min date
Set `min=` to specify a minimum date.
```py
date = view(box('Pick a date', mode='day', value='2021-10-10', min='2019-01-01'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def day_min(view: View):
    date = view_output(view, day_min_docs, box('Pick a date', mode='day', value='2021-10-10', min='2019-01-01'))
    view_output(view, day_min_docs, f'You picked {date}.')


day_max_docs = (
"""
## Calendar - Set max date
Set `max=` to specify a maximum date.
```py
date = view(box('Pick a date', mode='day', value='2021-10-10', max='2022-12-31'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def day_max(view: View):
    date = view_output(view, day_max_docs, box('Pick a date', mode='day', value='2021-10-10', max='2022-12-31'))
    view_output(view, day_max_docs, f'You picked {date}.')


day_min_max_docs = (
"""
## Calendar - Combine min and max dates
Set both `min=` and `max=` to restrict selection between two dates.
```py
date = view(box('Pick a date', mode='day', value='2021-10-10', min='2019-01-01', max='2022-12-31'))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def day_min_max(view: View):
    date = view_output(view, day_min_max_docs, box('Pick a date', mode='day', value='2021-10-10', min='2019-01-01', max='2022-12-31'))
    view_output(view, day_min_max_docs, f'You picked {date}.')


day_range_docs = (
"""
## Calendar - Set range
Set `range=` to a `(min, max)` tuple to restrict selection between two dates.

This is a shorthand notation for setting `min=` and `max=` individually.
```py
date = view(box('Pick a date', mode='day', value='2021-10-10', range=('2019-01-01', '2022-12-31')))
view(f'You picked {date}.')
```
""",
    '### Output',
)


def day_range(view: View):
    date = view_output(view, day_range_docs, box('Pick a date', mode='day', value='2021-10-10', range=('2019-01-01', '2022-12-31')))
    view_output(view, day_range_docs, f'You picked {date}.')


week_basic_docs = (
"""
## Week Picker - Basic
Set `mode='week'` to show a week picker.
```py
week = view(box('Pick a week', mode='week'))
view(f'You picked {week}.')
```
""",
    '### Output',
)


def week_basic(view: View):
    week = view_output(view, week_basic_docs, box('Pick a week', mode='week'))
    view_output(view, week_basic_docs, f'You picked {week}.')


week_value_docs = (
"""
## Week Picker - Set initial week
Set `value=` to pre-select a week.

Dates must be in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format.
Date-only strings (e.g. "1970-01-01") are treated as UTC, not local.
```py
week = view(box('Pick a week', mode='week', value='2021-10-10'))
view(f'You picked {week}.')
```
""",
    '### Output',
)


def week_value(view: View):
    week = view_output(view, week_value_docs, box('Pick a week', mode='week', value='2021-10-10'))
    view_output(view, week_value_docs, f'You picked {week}.')


week_min_docs = (
"""
## Week Picker - Set min date
Set `min=` to specify a minimum date.
```py
week = view(box('Pick a week', mode='week', value='2021-10-10', min='2019-01-01'))
view(f'You picked {week}.')
```
""",
    '### Output',
)


def week_min(view: View):
    week = view_output(view, week_min_docs, box('Pick a week', mode='week', value='2021-10-10', min='2019-01-01'))
    view_output(view, week_min_docs, f'You picked {week}.')


week_max_docs = (
"""
## Week Picker - Set max date
Set `max=` to specify a maximum date.
```py
week = view(box('Pick a week', mode='week', value='2021-10-10', max='2022-12-31'))
view(f'You picked {week}.')
```
""",
    '### Output',
)


def week_max(view: View):
    week = view_output(view, week_max_docs, box('Pick a week', mode='week', value='2021-10-10', max='2022-12-31'))
    view_output(view, week_max_docs, f'You picked {week}.')


week_min_max_docs = (
"""
## Week Picker - Combine min and max dates
Set both `min=` and `max=` to restrict selection between two dates.
```py
week = view(box('Pick a week', mode='week', value='2021-10-10', min='2019-01-01', max='2022-12-31'))
view(f'You picked {week}.')
```
""",
    '### Output',
)


def week_min_max(view: View):
    week = view_output(view, week_min_max_docs, box('Pick a week', mode='week', value='2021-10-10', min='2019-01-01', max='2022-12-31'))
    view_output(view, week_min_max_docs, f'You picked {week}.')


week_range_docs = (
"""
## Week Picker - Set range
Set `range=` to a `(min, max)` tuple to restrict selection between two dates.

This is a shorthand notation for setting `min=` and `max=` individually.
```py
week = view(box('Pick a week', mode='week', value='2021-10-10', range=('2019-01-01', '2022-12-31')))
view(f'You picked {week}.')
```
""",
    '### Output',
)


def week_range(view: View):
    week = view_output(view, week_range_docs, box('Pick a week', mode='week', value='2021-10-10', range=('2019-01-01', '2022-12-31')))
    view_output(view, week_range_docs, f'You picked {week}.')


month_basic_docs = (
"""
## Month Picker - Basic
Set `mode='month'` to show a month picker.
```py
month = view(box('Pick a month', mode='month'))
view(f'You picked {month}.')
```
""",
    '### Output',
)


def month_basic(view: View):
    month = view_output(view, month_basic_docs, box('Pick a month', mode='month'))
    view_output(view, month_basic_docs, f'You picked {month}.')


month_value_docs = (
"""
## Month Picker - Set initial month
Set `value=` to pre-select a month.

Dates must be in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format.
Date-only strings (e.g. "1970-01-01") are treated as UTC, not local.
```py
month = view(box('Pick a month', mode='month', value='2021-10-10'))
view(f'You picked {month}.')
```
""",
    '### Output',
)


def month_value(view: View):
    month = view_output(view, month_value_docs, box('Pick a month', mode='month', value='2021-10-10'))
    view_output(view, month_value_docs, f'You picked {month}.')


month_min_docs = (
"""
## Month Picker - Set min date
Set `min=` to specify a minimum date.
```py
month = view(box('Pick a month', mode='month', value='2021-10-10', min='2019-01-01'))
view(f'You picked {month}.')
```
""",
    '### Output',
)


def month_min(view: View):
    month = view_output(view, month_min_docs, box('Pick a month', mode='month', value='2021-10-10', min='2019-01-01'))
    view_output(view, month_min_docs, f'You picked {month}.')


month_max_docs = (
"""
## Month Picker - Set max date
Set `max=` to specify a maximum date.
```py
month = view(box('Pick a month', mode='month', value='2021-10-10', max='2022-12-31'))
view(f'You picked {month}.')
```
""",
    '### Output',
)


def month_max(view: View):
    month = view_output(view, month_max_docs, box('Pick a month', mode='month', value='2021-10-10', max='2022-12-31'))
    view_output(view, month_max_docs, f'You picked {month}.')


month_min_max_docs = (
"""
## Month Picker - Combine min and max dates
Set both `min=` and `max=` to restrict selection between two dates.
```py
month = view(box('Pick a month', mode='month', value='2021-10-10', min='2019-01-01', max='2022-12-31'))
view(f'You picked {month}.')
```
""",
    '### Output',
)


def month_min_max(view: View):
    month = view_output(view, month_min_max_docs, box('Pick a month', mode='month', value='2021-10-10', min='2019-01-01', max='2022-12-31'))
    view_output(view, month_min_max_docs, f'You picked {month}.')


month_range_docs = (
"""
## Month Picker - Set range
Set `range=` to a `(min, max)` tuple to restrict selection between two dates.

This is a shorthand notation for setting `min=` and `max=` individually.
```py
month = view(box('Pick a month', mode='month', value='2021-10-10', range=('2019-01-01', '2022-12-31')))
view(f'You picked {month}.')
```
""",
    '### Output',
)


def month_range(view: View):
    month = view_output(view, month_range_docs, box('Pick a month', mode='month', value='2021-10-10', range=('2019-01-01', '2022-12-31')))
    view_output(view, month_range_docs, f'You picked {month}.')


tag_picker_basic_docs = (
"""
## Tag Picker - Basic
Set `mode='tag'` to display a tag picker. `multiple=True` is implied.
```py
tags = view(box(
    'Choose some tags',
    mode='tag',
    options=['violet', 'indigo', 'blue', 'green', 'yellow', 'orange', 'red']
))
view(f'You chose {tags}.')
```
""",
    '### Output',
)


def tag_picker_basic(view: View):
    tags = view_output(view, tag_picker_basic_docs, box(
        'Choose some tags',
        mode='tag',
        options=['violet', 'indigo', 'blue', 'green', 'yellow', 'orange', 'red']
    ))
    view_output(view, tag_picker_basic_docs, f'You chose {tags}.')


tag_picker_value_docs = (
"""
## Tag Picker - Set initial tags
Set `value=` to pre-select options having those values.
```py
tags = view(box(
    'Choose some tags',
    mode='tag',
    value=['yellow', 'red'],
    options=['violet', 'indigo', 'blue', 'green', 'yellow', 'orange', 'red']
))
view(f'You chose {tags}.')
```
""",
    '### Output',
)


def tag_picker_value(view: View):
    tags = view_output(view, tag_picker_value_docs, box(
        'Choose some tags',
        mode='tag',
        value=['yellow', 'red'],
        options=['violet', 'indigo', 'blue', 'green', 'yellow', 'orange', 'red']
    ))
    view_output(view, tag_picker_value_docs, f'You chose {tags}.')


tag_picker_selected_docs = (
"""
## Tag Picker - Mark tags as selected
Set `selected=True` to pre-select one or more options.
```py
tags = view(box('Choose some tags', mode='tag', options=[
    option('violet', 'Violet'),
    option('indigo', 'Indigo'),
    option('blue', 'Blue'),
    option('green', 'Green'),
    option('yellow', 'Yellow', selected=True),
    option('orange', 'Orange'),
    option('red', 'Red', selected=True),
]))
view(f'You chose {tags}.')
```
""",
    '### Output',
)


def tag_picker_selected(view: View):
    tags = view_output(view, tag_picker_selected_docs, box('Choose some tags', mode='tag', options=[
        option('violet', 'Violet'),
        option('indigo', 'Indigo'),
        option('blue', 'Blue'),
        option('green', 'Green'),
        option('yellow', 'Yellow', selected=True),
        option('orange', 'Orange'),
        option('red', 'Red', selected=True),
    ]))
    view_output(view, tag_picker_selected_docs, f'You chose {tags}.')


color_basic_docs = (
"""
## Color Picker - Basic
Set `mode='color'` to show a color picker.

The return value is a `(r, g, b, a)` tuple,
where `r`, `g`, `b` are integers between 0-255,
and `a` is an integer between 0-100%.
```py
color = view(box('Choose a color', mode='color'))
r, g, b, a = color
view(f'You chose the color `rgba({r}, {g}, {b}, {a}%)`.')
```
""",
    '### Output',
)


def color_basic(view: View):
    color = view_output(view, color_basic_docs, box('Choose a color', mode='color'))
    r, g, b, a = color
    view_output(view, color_basic_docs, f'You chose the color `rgba({r}, {g}, {b}, {a}%)`.')


color_value_docs = (
"""
## Color Picker - Set initial color
Set `value=` to set the initial color.

A color value can be:

- `#RRGGBB` e.g. `#ff0033`
- `#RRGGBBAA` e.g. `#ff003388`
- `#RGB` e.g. `#f03` (same as `#ff0033`)
- `#RGBA` e.g. `#f038` (same as `#ff003388`)
- `rgb(R,G,B)` e.g. `rgb(255, 0, 127)` or `rgb(100%, 0%, 50%)`
- `rgba(R,G,B,A)` e.g. `rgb(255, 0, 127, 0.5)` or `rgb(100%, 0%, 50%, 50%)`
- `hsl(H,S,L)` e.g. `hsl(348, 100%, 50%)`
- `hsl(H,S,L,A)` e.g. `hsl(348, 100%, 50%, 0.5)` or `hsl(348, 100%, 50%, 50%)`
- A [named color](https://drafts.csswg.org/css-color-3/#svg-color) e.g. `red`, `green`, `blue`, etc.
- `transparent` (same as `rgba(0,0,0,0)`)

The return value, as in the previous example, is a `(r, g, b, a)` tuple.
```py
color = view(box('Choose a color', mode='color', value='#a241e8'))
view(f'You chose {color}.')
```
""",
    '### Output',
)


def color_value(view: View):
    color = view_output(view, color_value_docs, box('Choose a color', mode='color', value='#a241e8'))
    view_output(view, color_value_docs, f'You chose {color}.')


palette_basic_docs = (
"""
## Color Palette - Basic
Set `options=` with `mode='color'` to show a color palette.

The option's `value` must be a valid color in one of the formats described in the previous example.

Unlike the Color Picker, the Color Palette returns the `value` of the chosen option, and not a `(r,g,b,a)` tuple.
```py
color = view(box('Choose a color', mode='color', options=[
    option('#ff0000', 'Red'),
    option('#00ff00', 'Green'),
    option('#0000ff', 'Blue'),
    option('#ffff00', 'Yellow'),
    option('#00ffff', 'Cyan'),
    option('#ff00ff', 'Magenta'),
]))
view(f'You chose {color}.')
```
""",
    '### Output',
)


def palette_basic(view: View):
    color = view_output(view, palette_basic_docs, box('Choose a color', mode='color', options=[
        option('#ff0000', 'Red'),
        option('#00ff00', 'Green'),
        option('#0000ff', 'Blue'),
        option('#ffff00', 'Yellow'),
        option('#00ffff', 'Cyan'),
        option('#ff00ff', 'Magenta'),
    ]))
    view_output(view, palette_basic_docs, f'You chose {color}.')


palette_value_docs = (
"""
## Color Palette - Set initial color
Set `value=` to pre-select an option having that color value.
```py
color = view(box('Choose a color', mode='color', value='#0000ff', options=[
    option('#ff0000', 'Red'),
    option('#00ff00', 'Green'),
    option('#0000ff', 'Blue'),
    option('#ffff00', 'Yellow'),
    option('#00ffff', 'Cyan'),
    option('#ff00ff', 'Magenta'),
]))
view(f'You chose {color}.')
```
""",
    '### Output',
)


def palette_value(view: View):
    color = view_output(view, palette_value_docs, box('Choose a color', mode='color', value='#0000ff', options=[
        option('#ff0000', 'Red'),
        option('#00ff00', 'Green'),
        option('#0000ff', 'Blue'),
        option('#ffff00', 'Yellow'),
        option('#00ffff', 'Cyan'),
        option('#ff00ff', 'Magenta'),
    ]))
    view_output(view, palette_value_docs, f'You chose {color}.')


palette_selected_docs = (
"""
## Color Palette - Mark colors as selected
Alternatively, set `selected=True` to pre-select a color in the palette.
```py
color = view(box('Choose a color', mode='color', options=[
    option('#ff0000', 'Red'),
    option('#00ff00', 'Green'),
    option('#0000ff', 'Blue', selected=True),
    option('#ffff00', 'Yellow'),
    option('#00ffff', 'Cyan'),
    option('#ff00ff', 'Magenta'),
]))
view(f'You chose {color}.')
```
""",
    '### Output',
)


def palette_selected(view: View):
    color = view_output(view, palette_selected_docs, box('Choose a color', mode='color', options=[
        option('#ff0000', 'Red'),
        option('#00ff00', 'Green'),
        option('#0000ff', 'Blue', selected=True),
        option('#ffff00', 'Yellow'),
        option('#00ffff', 'Cyan'),
        option('#ff00ff', 'Magenta'),
    ]))
    view_output(view, palette_selected_docs, f'You chose {color}.')


rating_basic_docs = (
"""
## Rating - Basic
Set `mode='rating'` to accept a star-rating.

By default, five stars are displayed.
```py
stars = view(box('Rate your experience', mode='rating'))
view(f'Your rating was {stars} stars.')
```
""",
    '### Output',
)


def rating_basic(view: View):
    stars = view_output(view, rating_basic_docs, box('Rate your experience', mode='rating'))
    view_output(view, rating_basic_docs, f'Your rating was {stars} stars.')


rating_value_docs = (
"""
## Rating - Set initial rating
Set `value=` to specify a default value.
```py
stars = view(box('Rate your experience', mode='rating', value=3))
view(f'Your rating was {stars} stars.')
```
""",
    '### Output',
)


def rating_value(view: View):
    stars = view_output(view, rating_value_docs, box('Rate your experience', mode='rating', value=3))
    view_output(view, rating_value_docs, f'Your rating was {stars} stars.')


rating_min_docs = (
"""
## Rating - Allow zero stars
Set `min=0` to allow zero stars.
```py
stars = view(box('Rate your experience', mode='rating', min=0))
view(f'Your rating was {stars} stars.')
```
""",
    '### Output',
)


def rating_min(view: View):
    stars = view_output(view, rating_min_docs, box('Rate your experience', mode='rating', min=0))
    view_output(view, rating_min_docs, f'Your rating was {stars} stars.')


rating_max_docs = (
"""
## Rating - Set maximum number of stars
Set `max=` to increase the number of stars displayed.
```py
stars = view(box('Rate your experience', mode='rating', value=3, max=10))
view(f'Your rating was {stars} stars.')
```
""",
    '### Output',
)


def rating_max(view: View):
    stars = view_output(view, rating_max_docs, box('Rate your experience', mode='rating', value=3, max=10))
    view_output(view, rating_max_docs, f'Your rating was {stars} stars.')


rating_min_max_docs = (
"""
## Rating - Combine min and max stars
`min=` and `max=` can be combined.
```py
stars = view(box('Rate your experience', mode='rating', value=3, min=0, max=10))
view(f'Your rating was {stars} stars.')
```
""",
    '### Output',
)


def rating_min_max(view: View):
    stars = view_output(view, rating_min_max_docs, box('Rate your experience', mode='rating', value=3, min=0, max=10))
    view_output(view, rating_min_max_docs, f'Your rating was {stars} stars.')


rating_range_docs = (
"""
## Rating - Set range
Set `range=` to a `(min, max)` tuple to control min/max stars.

This is a shorthand notation for setting `min=` and `max=` individually.
```py
stars = view(box('Rate your experience', mode='rating', value=3, range=(0, 10)))
view(f'Your rating was {stars} stars.')
```
""",
    '### Output',
)


def rating_range(view: View):
    stars = view_output(view, rating_range_docs, box('Rate your experience', mode='rating', value=3, range=(0, 10)))
    view_output(view, rating_range_docs, f'Your rating was {stars} stars.')


file_upload_basic_docs = (
"""
## File Upload - Basic
Set `mode='file'` to show a file upload box.

For file uploads to work correctly, you must define a file upload handler in your
Django, Flask, Starlette, or Tornado application.

The file upload box sends a `multipart/form-data` HTTP `POST` request to the upload
path  (`/upload` by default). The uploaded files are each named `file`. The handler
is expected to process the files and return a JSON response containing a string
array named `files`. This array is returned as-is by `view()` to your Nitro
application code.
```py
filename = view(box('Upload a document', mode='file'))
view(f'You uploaded {filename}.')
```
""",
    '### Output',
)


def file_upload_basic(view: View):
    filename = view_output(view, file_upload_basic_docs, box('Upload a document', mode='file'))
    view_output(view, file_upload_basic_docs, f'You uploaded {filename}.')


file_upload_multiple_docs = (
"""
## File Upload - Allow multiple files
Set `multiple=True` to allow uploading multiple files.
```py
filenames = view(box('Upload some documents', mode='file', multiple=True))
view(f'You uploaded {filenames}.')
```
""",
    '### Output',
)


def file_upload_multiple(view: View):
    filenames = view_output(view, file_upload_multiple_docs, box('Upload some documents', mode='file', multiple=True))
    view_output(view, file_upload_multiple_docs, f'You uploaded {filenames}.')


file_upload_path_docs = (
"""
## File Upload - Set upload path
Set `path=` to set the path to upload files to.

This is useful if your app's file upload handler path is different from `/upload` (the default),
```py
filename = view(box('Upload a document', mode='file', path='/upload'))
view(f'You uploaded {filename}.')
```
""",
    '### Output',
)


def file_upload_path(view: View):
    filename = view_output(view, file_upload_path_docs, box('Upload a document', mode='file', path='/upload'))
    view_output(view, file_upload_path_docs, f'You uploaded {filename}.')


separator_basic_docs = (
"""
## Separator - Basic
Call `box()` with `mode='separator'` to show a separator.
```py
view(box('Donuts', mode='separator'))
```
""",
    '### Output',
)


def separator_basic(view: View):
    view_output(view, separator_basic_docs, box('Donuts', mode='separator'))


separator_align_docs = (
"""
## Separator - Set text alignment
A separator's label is centered by default.
Set `align=` to left- or right-align the label.
```py
view(
    box('Left-aligned', mode='separator', align='left'),
    box(lorem(3)),
    box('Center-aligned', mode='separator'),
    box(lorem(3)),
    box('Right-aligned', mode='separator', align='right'),
    box(lorem(3)),
)
```
""",
    '### Output',
)


def separator_align(view: View):
    view_output(view, separator_align_docs, 
        box('Left-aligned', mode='separator', align='left'),
        box(lorem(3)),
        box('Center-aligned', mode='separator'),
        box(lorem(3)),
        box('Right-aligned', mode='separator', align='right'),
        box(lorem(3)),
    )


theme_basic_noop_docs = (
"""
## Theming - Set initial theme
Pass `theme=` when creating the app's `View()`.

Use `Theme()` to define a theme.
- `background_color` sets the color of the page background.
- `foreground_color` sets the color of the page text.
- `accent_color` sets the accent color.
- `accent_color_name` describes the accent color.

`accent_color_name` must be one of `red`, `lava`, `orange`, `amber`, `yellow`, `lime`, `mint`, `green`, `teal`,
`cyan`, `sky`, `blue`, `indigo`, `purple`, `violet`, or `pink`.
This is used to automatically pick matching spectrum colors, useful for visualizations and infographics.
```py
# App entry point
def main(view: View):
    pass

# Create theme
my_theme = Theme(
    background_color='#fff',
    foreground_color='#3e3f4a',
    accent_color='#ef534f',
    accent_color_name='green'
)

# Set theme when creating the View()
nitro = View(main, title='My App', caption='v1.0', theme=my_theme)

```
""",
)


def theme_basic_noop(view: View):
    # App entry point
    def main(view: View):
        pass

    # Create theme
    my_theme = Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#ef534f',
        accent_color_name='green'
    )

    # Set theme when creating the View()
    nitro = View(main, title='My App', caption='v1.0', theme=my_theme)

    view_output(view, theme_basic_noop_docs, )


theme_switching_docs = (
"""
## Theming - Switch theme dynamically
Use `view.set(theme=)` to change the theme dynamically.

This is useful when you want to allow the app's end-users to switch app's theme.
```py
make_red = False
while True:
    make_red, done = view(
        box('Apply red theme', mode='toggle', value=make_red),
        box(['Done'])
    )

    if done:
        break

    if make_red:
        view.set(theme=Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#ef534f',
            accent_color_name='red'
        ))
    else:
        view.set(theme=Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#5a64f0',
            accent_color_name='indigo'
        ))
```
""",
    '### Output',
)


def theme_switching(view: View):
    make_red = False
    while True:
        make_red, done = view_output(view, theme_switching_docs, 
            box('Apply red theme', mode='toggle', value=make_red),
            box(['Done'])
        )

        if done:
            break

        if make_red:
            view.set(theme=Theme(
                background_color='#fff',
                foreground_color='#3e3f4a',
                accent_color='#ef534f',
                accent_color_name='red'
            ))
        else:
            view.set(theme=Theme(
                background_color='#fff',
                foreground_color='#3e3f4a',
                accent_color='#5a64f0',
                accent_color_name='indigo'
            ))


theme_dark_mode_docs = (
"""
## Theming - Dark mode
A simple way to allow switching between dark and light modes is to exchange the `background_color` and
`foreground_color` in the theme, provided the `accent_color` works with both dark and light backgrounds.
```py
dark_mode = False
while True:
    dark_mode, done = view(
        box('Dark Mode', mode='toggle', value=dark_mode),
        box(['Done'])
    )

    if done:
        break

    if dark_mode:
        view.set(theme=Theme(
            background_color='#3e3f4a',  # dark background
            foreground_color='#fff',  # light foreground
            accent_color='#ef534f',
            accent_color_name='red'
        ))
    else:
        view.set(theme=Theme(
            background_color='#fff',  # light background
            foreground_color='#3e3f4a',  # dark foreground
            accent_color='#ef534f',
            accent_color_name='red'
        ))
```
""",
    '### Output',
)


def theme_dark_mode(view: View):
    dark_mode = False
    while True:
        dark_mode, done = view_output(view, theme_dark_mode_docs, 
            box('Dark Mode', mode='toggle', value=dark_mode),
            box(['Done'])
        )

        if done:
            break

        if dark_mode:
            view.set(theme=Theme(
                background_color='#3e3f4a',  # dark background
                foreground_color='#fff',  # light foreground
                accent_color='#ef534f',
                accent_color_name='red'
            ))
        else:
            view.set(theme=Theme(
                background_color='#fff',  # light background
                foreground_color='#3e3f4a',  # dark foreground
                accent_color='#ef534f',
                accent_color_name='red'
            ))


theme_colors_docs = (
"""
## Theming - Use color variables
*Color variables* are pre-defined, named colors that match the app's theme.

Color variables take the form `var(--name)`, or simply `$name`. For example, you can use
`var(--red)` or `$red` instead of hard-coded colors like `red` or `#ff0000` or `rgb(255,0,0)`.

Color variables can be passed wherever colors are accepted, like `background=`, `border=`, `color=`, and so on.

There are 16 pre-defined *spectrum colors*, derived automatically from the theme's accent color by matching its
saturation and lightness. Spectrum colors are useful for data visualizations and infographics. The naming of each
color is only indicative, and its hue might appear off depending on the position of the accent color's hue along the
color spectrum. For example, `$red` could appear pink or orange!

Additionally, there are pre-defined color variables for various *tones* of the theme's foreground (`$foreground`),
background (`$background`) and accent (`$accent`) colors.
Accent tones are prefixed with `$accent-`, and neutral tones (grays) are prefixed with `$neutral-`.
```py
style = dict(width=30, height=30, border='#777', margin='0 0 2.5rem 0')
view(
    '### Spectrum Colors',
    row(
        box(background='$red', **style),
        box(background='$lava', **style),
        box(background='$orange', **style),
        box(background='$amber', **style),
        box(background='$yellow', **style),
        box(background='$lime', **style),
        box(background='$mint', **style),
        box(background='$green', **style),
        box(background='$teal', **style),
        box(background='$cyan', **style),
        box(background='$sky', **style),
        box(background='$blue', **style),
        box(background='$indigo', **style),
        box(background='$purple', **style),
        box(background='$violet', **style),
        box(background='$pink', **style),
        wrap='normal',
    ),
    '### Theme Colors',
    row(
        box(background='$foreground', **style),
        box(background='$background', **style),
        box(background='$accent', **style),
        wrap='normal',
    ),
    '### Accent Tones',
    row(
        box(background='$accent-darker', **style),
        box(background='$accent-dark', **style),
        box(background='$accent-dark-alt', **style),
        box(background='$accent-primary', **style),
        box(background='$accent-secondary', **style),
        box(background='$accent-tertiary', **style),
        box(background='$accent-light', **style),
        box(background='$accent-lighter', **style),
        box(background='$accent-lighter-alt', **style),
        wrap='normal',
    ),
    '### Neutral Tones',
    row(
        box(background='$neutral-dark', **style),
        box(background='$neutral-primary', **style),
        box(background='$neutral-primary-alt', **style),
        box(background='$neutral-secondary', **style),
        box(background='$neutral-secondary-alt', **style),
        box(background='$neutral-tertiary', **style),
        box(background='$neutral-tertiary-alt', **style),
        box(background='$neutral-quaternary', **style),
        box(background='$neutral-quaternary-alt', **style),
        box(background='$neutral-light', **style),
        box(background='$neutral-lighter', **style),
        box(background='$neutral-lighter-alt', **style),
        wrap='normal',
    ),
)
```
""",
    '### Output',
)


def theme_colors(view: View):
    style = dict(width=30, height=30, border='#777', margin='0 0 2.5rem 0')
    view_output(view, theme_colors_docs, 
        '### Spectrum Colors',
        row(
            box(background='$red', **style),
            box(background='$lava', **style),
            box(background='$orange', **style),
            box(background='$amber', **style),
            box(background='$yellow', **style),
            box(background='$lime', **style),
            box(background='$mint', **style),
            box(background='$green', **style),
            box(background='$teal', **style),
            box(background='$cyan', **style),
            box(background='$sky', **style),
            box(background='$blue', **style),
            box(background='$indigo', **style),
            box(background='$purple', **style),
            box(background='$violet', **style),
            box(background='$pink', **style),
            wrap='normal',
        ),
        '### Theme Colors',
        row(
            box(background='$foreground', **style),
            box(background='$background', **style),
            box(background='$accent', **style),
            wrap='normal',
        ),
        '### Accent Tones',
        row(
            box(background='$accent-darker', **style),
            box(background='$accent-dark', **style),
            box(background='$accent-dark-alt', **style),
            box(background='$accent-primary', **style),
            box(background='$accent-secondary', **style),
            box(background='$accent-tertiary', **style),
            box(background='$accent-light', **style),
            box(background='$accent-lighter', **style),
            box(background='$accent-lighter-alt', **style),
            wrap='normal',
        ),
        '### Neutral Tones',
        row(
            box(background='$neutral-dark', **style),
            box(background='$neutral-primary', **style),
            box(background='$neutral-primary-alt', **style),
            box(background='$neutral-secondary', **style),
            box(background='$neutral-secondary-alt', **style),
            box(background='$neutral-tertiary', **style),
            box(background='$neutral-tertiary-alt', **style),
            box(background='$neutral-quaternary', **style),
            box(background='$neutral-quaternary-alt', **style),
            box(background='$neutral-light', **style),
            box(background='$neutral-lighter', **style),
            box(background='$neutral-lighter-alt', **style),
            wrap='normal',
        ),
    )


theme_samples_docs = (
"""
## Theming - Some sample themes
This example provides some sample themes that you can use in your own app.
```py
themes = [
    Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#ef5350',
        accent_color_name='red',
    ),
    Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#ec407a',
        accent_color_name='pink',
    ),
    Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#ab47bc',
        accent_color_name='violet',
    ),
    Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#7e57c2',
        accent_color_name='purple',
    ),
    Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#5c6bc0',
        accent_color_name='indigo',
    ),
    Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#42a5f5',
        accent_color_name='blue',
    ),
    Theme(
        background_color='#3e3f4a',
        foreground_color='#fff',
        accent_color='#29b6f6',
        accent_color_name='sky',
    ),
    Theme(
        background_color='#3e3f4a',
        foreground_color='#fff',
        accent_color='#26c6da',
        accent_color_name='cyan',
    ),
    Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#26a69a',
        accent_color_name='teal',
    ),
    Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#66bb6a',
        accent_color_name='green',
    ),
    Theme(
        background_color='#3e3f4a',
        foreground_color='#fff',
        accent_color='#9ccc65',
        accent_color_name='mint',
    ),
    Theme(
        background_color='#3e3f4a',
        foreground_color='#fff',
        accent_color='#d4e157',
        accent_color_name='lime',
    ),
    Theme(
        background_color='#3e3f4a',
        foreground_color='#fff',
        accent_color='#ffee58',
        accent_color_name='yellow',
    ),
    Theme(
        background_color='#3e3f4a',
        foreground_color='#fff',
        accent_color='#ffca28',
        accent_color_name='amber',
    ),
    Theme(
        background_color='#3e3f4a',
        foreground_color='#fff',
        accent_color='#ffa726',
        accent_color_name='orange',
    ),
    Theme(
        background_color='#fff',
        foreground_color='#3e3f4a',
        accent_color='#ff7043',
        accent_color_name='lava',
    ),
]

theme_lookup = {theme.accent_color_name: theme for theme in themes}
theme_names = list(theme_lookup.keys())
theme_names.sort()
theme_name = theme_names[0]

while True:
    response = view(
        box('Pick a theme', value=theme_name, options=theme_names),
        col(
            # Sample fields
            box('Enter text', placeholder='Enter some text'),
            box('Enter a number', value=42),
            box('Check this', mode='check', value=True),
            box('Toggle this', mode='toggle', value=True),
            box('Are you sure?', mode='radio', options=['Yes', 'No']),
            box('Pick a flavor', mode='menu', options=['Chocolate', 'Vanilla'], value='Chocolate'),
            box('Pick a value', mode='range', value=42, range=(0, 100)),
            box('Pick a day', mode='day'),
            box('Rate this', mode='rating'),
            padding='2rem', border='$neutral-tertiary'
        ),
        box(['Apply Theme', 'Done'])
    )
    theme_name = response[0]
    action = response[len(response) - 1]

    if action == 'Done':
        break
    view.set(theme=theme_lookup.get(theme_name))
```
""",
    '### Output',
)


def theme_samples(view: View):
    themes = [
        Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#ef5350',
            accent_color_name='red',
        ),
        Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#ec407a',
            accent_color_name='pink',
        ),
        Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#ab47bc',
            accent_color_name='violet',
        ),
        Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#7e57c2',
            accent_color_name='purple',
        ),
        Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#5c6bc0',
            accent_color_name='indigo',
        ),
        Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#42a5f5',
            accent_color_name='blue',
        ),
        Theme(
            background_color='#3e3f4a',
            foreground_color='#fff',
            accent_color='#29b6f6',
            accent_color_name='sky',
        ),
        Theme(
            background_color='#3e3f4a',
            foreground_color='#fff',
            accent_color='#26c6da',
            accent_color_name='cyan',
        ),
        Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#26a69a',
            accent_color_name='teal',
        ),
        Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#66bb6a',
            accent_color_name='green',
        ),
        Theme(
            background_color='#3e3f4a',
            foreground_color='#fff',
            accent_color='#9ccc65',
            accent_color_name='mint',
        ),
        Theme(
            background_color='#3e3f4a',
            foreground_color='#fff',
            accent_color='#d4e157',
            accent_color_name='lime',
        ),
        Theme(
            background_color='#3e3f4a',
            foreground_color='#fff',
            accent_color='#ffee58',
            accent_color_name='yellow',
        ),
        Theme(
            background_color='#3e3f4a',
            foreground_color='#fff',
            accent_color='#ffca28',
            accent_color_name='amber',
        ),
        Theme(
            background_color='#3e3f4a',
            foreground_color='#fff',
            accent_color='#ffa726',
            accent_color_name='orange',
        ),
        Theme(
            background_color='#fff',
            foreground_color='#3e3f4a',
            accent_color='#ff7043',
            accent_color_name='lava',
        ),
    ]

    theme_lookup = {theme.accent_color_name: theme for theme in themes}
    theme_names = list(theme_lookup.keys())
    theme_names.sort()
    theme_name = theme_names[0]

    while True:
        response = view_output(view, theme_samples_docs, 
            box('Pick a theme', value=theme_name, options=theme_names),
            col(
                # Sample fields
                box('Enter text', placeholder='Enter some text'),
                box('Enter a number', value=42),
                box('Check this', mode='check', value=True),
                box('Toggle this', mode='toggle', value=True),
                box('Are you sure?', mode='radio', options=['Yes', 'No']),
                box('Pick a flavor', mode='menu', options=['Chocolate', 'Vanilla'], value='Chocolate'),
                box('Pick a value', mode='range', value=42, range=(0, 100)),
                box('Pick a day', mode='day'),
                box('Rate this', mode='rating'),
                padding='2rem', border='$neutral-tertiary'
            ),
            box(['Apply Theme', 'Done'])
        )
        theme_name = response[0]
        action = response[len(response) - 1]

        if action == 'Done':
            break
        view.set(theme=theme_lookup.get(theme_name))


layout_album_docs = (
"""
## Advanced Layout - An Album
A simple layout for photo galleries or portfolios.

Inspired by the [Bootstrap Album](https://getbootstrap.com/docs/4.0/examples/album/).
```py
def layout_album(view: View):
    cards = [make_album_card(lorem(1), i) for i in range(9)]

    view(
        col(
            box(f'## {lorem()}\\n\\n{lorem(3)}', align='center'),
            box(dict(yes='Primary', no='Secondary'), align='center'),
            color='$background', background='$foreground',
            padding='8rem', tile='center',
        ),
        row(
            *cards,
            background='$neutral-lighter',
            wrap='between', tile='center', padding='3rem'
        ),
        gap=0,
    )


def make_album_card(text, views):
    return col(
        box(image='image.png', height=200),
        box(text, padding='0 1rem'),
        row(
            box(mode='button', options=[
                option('view', 'View', selected=False, options=[
                    option('edit', 'Edit', icon='Edit')
                ])
            ]),
            box(f'{views + 1} views', align='right', color='$neutral-secondary'),
            padding='1rem', tile='between', cross_tile='end',
        ),
        background='$background', border='$neutral-tertiary-alt',
        padding=0, width='32%',
    )
```
""",
    '### Output',
)


def layout_album(view: View):
    cards = [make_album_card(lorem(1), i) for i in range(9)]

    view_output(view, layout_album_docs, 
        col(
            box(f'## {lorem()}\n\n{lorem(3)}', align='center'),
            box(dict(yes='Primary', no='Secondary'), align='center'),
            color='$background', background='$foreground',
            padding='8rem', tile='center',
        ),
        row(
            *cards,
            background='$neutral-lighter',
            wrap='between', tile='center', padding='3rem'
        ),
        gap=0,
    )


def make_album_card(text, views):
    return col(
        box(image='image.png', height=200),
        box(text, padding='0 1rem'),
        row(
            box(mode='button', options=[
                option('view', 'View', selected=False, options=[
                    option('edit', 'Edit', icon='Edit')
                ])
            ]),
            box(f'{views + 1} views', align='right', color='$neutral-secondary'),
            padding='1rem', tile='between', cross_tile='end',
        ),
        background='$background', border='$neutral-tertiary-alt',
        padding=0, width='32%',
    )


topics = dict(
    hello_world=hello_world,
    format_content=format_content,
    format_multiline_content=format_multiline_content,
    display_multiple=display_multiple,
    sequence_views=sequence_views,
    style_text=style_text,
    get_input=get_input,
    sequence_inputs=sequence_inputs,
    accept_multiple_inputs=accept_multiple_inputs,
    dunk_your_donuts=dunk_your_donuts,
    markdown_basic=markdown_basic,
    markdown_links=markdown_links,
    markdown_table=markdown_table,
    show_table=show_table,
    markdown_syntax_highlighting=markdown_syntax_highlighting,
    styling_background=styling_background,
    styling_color=styling_color,
    styling_border=styling_border,
    styling_align=styling_align,
    styling_size=styling_size,
    styling_margin=styling_margin,
    styling_padding=styling_padding,
    image_basic=image_basic,
    image_resize=image_resize,
    image_fit=image_fit,
    image_background=image_background,
    image_background_pattern=image_background_pattern,
    layout_basic=layout_basic,
    layout_row=layout_row,
    layout_col=layout_col,
    layout_tile=layout_tile,
    layout_cross_tile=layout_cross_tile,
    layout_gap=layout_gap,
    layout_wrap=layout_wrap,
    layout_grow_shrink=layout_grow_shrink,
    layout_vertical_alignment=layout_vertical_alignment,
    form_basic=form_basic,
    form_horizontal=form_horizontal,
    form_combo=form_combo,
    form_improved=form_improved,
    popup_basic=popup_basic,
    popup_title=popup_title,
    popup_buttons=popup_buttons,
    textbox_basic=textbox_basic,
    textbox_value=textbox_value,
    textbox_label=textbox_label,
    textbox_placeholder=textbox_placeholder,
    textbox_required=textbox_required,
    textbox_mask=textbox_mask,
    textbox_icon=textbox_icon,
    textbox_prefix=textbox_prefix,
    textbox_suffix=textbox_suffix,
    textbox_prefix_suffix=textbox_prefix_suffix,
    textbox_error=textbox_error,
    textbox_password=textbox_password,
    textarea=textarea,
    spinbox_basic=spinbox_basic,
    spinbox_value=spinbox_value,
    spinbox_min=spinbox_min,
    spinbox_max=spinbox_max,
    spinbox_step=spinbox_step,
    spinbox_precision=spinbox_precision,
    spinbox_range=spinbox_range,
    spinbox_range_alt=spinbox_range_alt,
    spinbox_range_alt_step=spinbox_range_alt_step,
    spinbox_range_alt_precision=spinbox_range_alt_precision,
    spinbox_negative=spinbox_negative,
    spinbox_decimal_step=spinbox_decimal_step,
    checkbox_basic=checkbox_basic,
    checkbox_value=checkbox_value,
    toggle_basic=toggle_basic,
    picker_basic=picker_basic,
    picker_buttons=picker_buttons,
    picker_radio=picker_radio,
    picker_dropdown=picker_dropdown,
    picker_multiple_dropdown=picker_multiple_dropdown,
    picker_checklist=picker_checklist,
    picker_dropdown_required=picker_dropdown_required,
    picker_dropdown_error=picker_dropdown_error,
    options_basic=options_basic,
    options_sequence=options_sequence,
    options_string=options_string,
    options_tuples=options_tuples,
    options_dict=options_dict,
    options_selected=options_selected,
    options_value=options_value,
    buttons_basic=buttons_basic,
    buttons_shorthand=buttons_shorthand,
    buttons_selected=buttons_selected,
    buttons_value=buttons_value,
    buttons_values=buttons_values,
    buttons_split=buttons_split,
    buttons_selected_split=buttons_selected_split,
    buttons_caption=buttons_caption,
    buttons_layout=buttons_layout,
    radio_basic=radio_basic,
    radio_value=radio_value,
    radio_selected=radio_selected,
    radio_icon=radio_icon,
    dropdown_basic=dropdown_basic,
    dropdown_value=dropdown_value,
    dropdown_selected=dropdown_selected,
    dropdown_grouped=dropdown_grouped,
    dropdown_editable=dropdown_editable,
    multi_dropdown_basic=multi_dropdown_basic,
    multi_dropdown_value=multi_dropdown_value,
    multi_dropdown_selected=multi_dropdown_selected,
    checklist_basic=checklist_basic,
    checklist_value=checklist_value,
    checklist_selected=checklist_selected,
    table_basic=table_basic,
    table_clickable=table_clickable,
    table_markdown=table_markdown,
    table_multiselect=table_multiselect,
    table_singleselect=table_singleselect,
    table_value=table_value,
    table_selected=table_selected,
    table_grouped=table_grouped,
    table_multilevel=table_multilevel,
    table_column_width=table_column_width,
    table_header_icon=table_header_icon,
    table_header_resizable=table_header_resizable,
    table_column_multiline=table_column_multiline,
    slider_basic=slider_basic,
    slider_value=slider_value,
    slider_min=slider_min,
    slider_max=slider_max,
    slider_step=slider_step,
    slider_precision=slider_precision,
    slider_range=slider_range,
    slider_range_alt=slider_range_alt,
    slider_range_alt_step=slider_range_alt_step,
    slider_range_alt_precision=slider_range_alt_precision,
    slider_negative=slider_negative,
    slider_decimal_step=slider_decimal_step,
    range_slider_basic=range_slider_basic,
    range_slider_min=range_slider_min,
    range_slider_max=range_slider_max,
    range_slider_step=range_slider_step,
    range_slider_precision=range_slider_precision,
    range_slider_range=range_slider_range,
    range_slider_range_alt=range_slider_range_alt,
    range_slider_range_alt_step=range_slider_range_alt_step,
    range_slider_range_alt_precision=range_slider_range_alt_precision,
    range_slider_negative=range_slider_negative,
    range_slider_decimal_step=range_slider_decimal_step,
    time_basic=time_basic,
    time_seconds=time_seconds,
    time_hour=time_hour,
    time_24=time_24,
    time_24_seconds=time_24_seconds,
    time_24_hour=time_24_hour,
    date_basic=date_basic,
    date_value=date_value,
    date_placeholder=date_placeholder,
    date_min=date_min,
    date_max=date_max,
    date_min_max=date_min_max,
    date_range=date_range,
    date_required=date_required,
    day_basic=day_basic,
    day_value=day_value,
    day_min=day_min,
    day_max=day_max,
    day_min_max=day_min_max,
    day_range=day_range,
    week_basic=week_basic,
    week_value=week_value,
    week_min=week_min,
    week_max=week_max,
    week_min_max=week_min_max,
    week_range=week_range,
    month_basic=month_basic,
    month_value=month_value,
    month_min=month_min,
    month_max=month_max,
    month_min_max=month_min_max,
    month_range=month_range,
    tag_picker_basic=tag_picker_basic,
    tag_picker_value=tag_picker_value,
    tag_picker_selected=tag_picker_selected,
    color_basic=color_basic,
    color_value=color_value,
    palette_basic=palette_basic,
    palette_value=palette_value,
    palette_selected=palette_selected,
    rating_basic=rating_basic,
    rating_value=rating_value,
    rating_min=rating_min,
    rating_max=rating_max,
    rating_min_max=rating_min_max,
    rating_range=rating_range,
    file_upload_basic=file_upload_basic,
    file_upload_multiple=file_upload_multiple,
    file_upload_path=file_upload_path,
    separator_basic=separator_basic,
    separator_align=separator_align,
    theme_basic_noop=theme_basic_noop,
    theme_switching=theme_switching,
    theme_dark_mode=theme_dark_mode,
    theme_colors=theme_colors,
    theme_samples=theme_samples,
    layout_album=layout_album,
)

table_of_contents = '''
# Welcome to Nitro!

Nitro is the simplest way to build interactive web apps using Python.
No front-end experience required.

This application is a collection of live, annotated examples for how to use
Nitro. It acts as a reference for how to do various things using Nitro, 
but can also be used as a guide to learn about many of the features Nitro provides.

You can always view an online version of these docs at [https://nitro.h2o.ai](https://nitro.h2o.ai).


### Basics

- [Hello World!](#hello_world)
- [Formatting content](#format_content)
- [Show multiline content](#format_multiline_content)
- [Show multiple items](#display_multiple)
- [Show multiple items, one at a time](#sequence_views)
- [Style text](#style_text)
- [Get user input](#get_input)
- [Get multiple inputs, one at a time](#sequence_inputs)
- [Get multiple inputs at once](#accept_multiple_inputs)
- [Putting it all together](#dunk_your_donuts)

### Markdown

- [Basics](#markdown_basic)
- [Handle clicks on links](#markdown_links)
- [Show tables](#markdown_table)
- [Create tables from lists](#show_table)
- [Syntax highlighting in code blocks](#markdown_syntax_highlighting)

### Styling

- [Set background color](#styling_background)
- [Set text color](#styling_color)
- [Set border color](#styling_border)
- [Set text alignment](#styling_align)
- [Set width and height](#styling_size)
- [Set margins](#styling_margin)
- [Set padding](#styling_padding)

### Images

- [Basic](#image_basic)
- [Set width and height](#image_resize)
- [Scale and clip images](#image_fit)
- [Use as background](#image_background)
- [Use as pattern](#image_background_pattern)

### Layout

- [Basics](#layout_basic)
- [Lay out horizontally](#layout_row)
- [Lay out vertically](#layout_col)
- [Control tiling](#layout_tile)
- [Control cross tiling](#layout_cross_tile)
- [Control spacing](#layout_gap)
- [Control wrapping](#layout_wrap)
- [Grow or shrink some items](#layout_grow_shrink)
- [Center content vertically](#layout_vertical_alignment)

### Forms

- [Basic](#form_basic)
- [Horizontal](#form_horizontal)
- [Combined](#form_combo)
- [Improved](#form_improved)

### Popups

- [Basic](#popup_basic)
- [Set popup title](#popup_title)
- [Customize buttons](#popup_buttons)

### Textbox

- [Basic](#textbox_basic)
- [Set initial value](#textbox_value)
- [Set a label](#textbox_label)
- [Show placeholder text](#textbox_placeholder)
- [Mark as required](#textbox_required)
- [Control input format](#textbox_mask)
- [Show an icon](#textbox_icon)
- [Set prefix text](#textbox_prefix)
- [Set suffix text](#textbox_suffix)
- [Set both prefix and suffix texts](#textbox_prefix_suffix)
- [Show an error message](#textbox_error)
- [Accept a password](#textbox_password)
- [Enable multiple lines](#textarea)

### Spinbox

- [Basic](#spinbox_basic)
- [Set initial value](#spinbox_value)
- [Set min value](#spinbox_min)
- [Set max value](#spinbox_max)
- [Set step](#spinbox_step)
- [Set precision](#spinbox_precision)
- [Combine min, max, step, precision](#spinbox_range)
- [Set range](#spinbox_range_alt)
- [Set range with step](#spinbox_range_alt_step)
- [Set range with precision](#spinbox_range_alt_precision)
- [Use zero-crossing ranges](#spinbox_negative)
- [Use fractional steps](#spinbox_decimal_step)

### Checkbox

- [Basic](#checkbox_basic)
- [Set initial value](#checkbox_value)

### Toggle

- [Basic](#toggle_basic)

### Pickers

- [Basic](#picker_basic)
- [Show buttons](#picker_buttons)
- [Show radio buttons](#picker_radio)
- [Show a dropdown menu](#picker_dropdown)
- [Show a dropdown list](#picker_multiple_dropdown)
- [Show a checklist](#picker_checklist)
- [Mark as required](#picker_dropdown_required)
- [Show an error message](#picker_dropdown_error)

### Options

- [Basic](#options_basic)
- [Create options from a sequence](#options_sequence)
- [Create options from a string](#options_string)
- [Create options from tuples](#options_tuples)
- [Create options from a dictionary](#options_dict)
- [Mark options as selected](#options_selected)
- [Set initial selection](#options_value)

### Buttons

- [Basic](#buttons_basic)
- [Shorthand notation](#buttons_shorthand)
- [Mark button as primary](#buttons_selected)
- [Select primary button](#buttons_value)
- [Select multiple primary buttons](#buttons_values)
- [Add a menu](#buttons_split)
- [Add a menu to a primary button](#buttons_selected_split)
- [Set a caption](#buttons_caption)
- [Lay out buttons vertically](#buttons_layout)

### Radio Buttons

- [Basic](#radio_basic)
- [Set initial selection](#radio_value)
- [Mark options as selected](#radio_selected)
- [Show pictorial options](#radio_icon)

### Dropdown

- [Basic](#dropdown_basic)
- [Set initial selection](#dropdown_value)
- [Mark options as selected](#dropdown_selected)
- [Group options](#dropdown_grouped)
- [Enable arbitrary input](#dropdown_editable)

### Dropdown List

- [Basic](#multi_dropdown_basic)
- [Set initial selection](#multi_dropdown_value)
- [Mark options as selected](#multi_dropdown_selected)

### Checklist

- [Basic](#checklist_basic)
- [Set initial selection](#checklist_value)
- [Mark options as checked](#checklist_selected)

### Table

- [Basic](#table_basic)
- [Make rows clickable](#table_clickable)
- [Use markdown in cells](#table_markdown)
- [Enable multi-select](#table_multiselect)
- [Enable single select](#table_singleselect)
- [Set initial selection](#table_value)
- [Mark rows as selected](#table_selected)
- [Group rows](#table_grouped)
- [Group rows at multiple levels](#table_multilevel)
- [Set column width](#table_column_width)
- [Set header icon](#table_header_icon)
- [Disable column resizing](#table_header_resizable)
- [Enable multiline cells](#table_column_multiline)

### Slider

- [Basic](#slider_basic)
- [Set initial value](#slider_value)
- [Set min value](#slider_min)
- [Set max value](#slider_max)
- [Set step](#slider_step)
- [Set precision](#slider_precision)
- [Combine min, max, step, precision](#slider_range)
- [Set range](#slider_range_alt)
- [Set range with step](#slider_range_alt_step)
- [Set range with precision](#slider_range_alt_precision)
- [Zero-crossing range](#slider_negative)
- [Set fractional steps](#slider_decimal_step)

### Range Slider

- [Basic](#range_slider_basic)
- [Set min value](#range_slider_min)
- [Set max value](#range_slider_max)
- [Set step](#range_slider_step)
- [Set precision](#range_slider_precision)
- [Combine min, max, step, precision](#range_slider_range)
- [Set range](#range_slider_range_alt)
- [Set range with step](#range_slider_range_alt_step)
- [Set range with precision](#range_slider_range_alt_precision)
- [Use zero-crossing range](#range_slider_negative)
- [Set fractional steps](#range_slider_decimal_step)

### Time Picker

- [Basic](#time_basic)
- [Enable seconds](#time_seconds)
- [Show hours only](#time_hour)
- [Show 24-hour clock](#time_24)
- [Show 24-hour clock, with seconds](#time_24_seconds)
- [Show 24-hour clock, with hour only](#time_24_hour)

### Date Picker

- [Basic](#date_basic)
- [Set initial date](#date_value)
- [Set placeholder text](#date_placeholder)
- [Set min date](#date_min)
- [Set max date](#date_max)
- [Combine min and max date](#date_min_max)
- [Set range](#date_range)
- [Mark as required](#date_required)

### Calendar

- [Basic](#day_basic)
- [Set initial date](#day_value)
- [Set min date](#day_min)
- [Set max date](#day_max)
- [Combine min and max dates](#day_min_max)
- [Set range](#day_range)

### Week Picker

- [Basic](#week_basic)
- [Set initial week](#week_value)
- [Set min date](#week_min)
- [Set max date](#week_max)
- [Combine min and max dates](#week_min_max)
- [Set range](#week_range)

### Month Picker

- [Basic](#month_basic)
- [Set initial month](#month_value)
- [Set min date](#month_min)
- [Set max date](#month_max)
- [Combine min and max dates](#month_min_max)
- [Set range](#month_range)

### Tag Picker

- [Basic](#tag_picker_basic)
- [Set initial tags](#tag_picker_value)
- [Mark tags as selected](#tag_picker_selected)

### Color Picker

- [Basic](#color_basic)
- [Set initial color](#color_value)

### Color Palette

- [Basic](#palette_basic)
- [Set initial color](#palette_value)
- [Mark colors as selected](#palette_selected)

### Rating

- [Basic](#rating_basic)
- [Set initial rating](#rating_value)
- [Allow zero stars](#rating_min)
- [Set maximum number of stars](#rating_max)
- [Combine min and max stars](#rating_min_max)
- [Set range](#rating_range)

### File Upload

- [Basic](#file_upload_basic)
- [Allow multiple files](#file_upload_multiple)
- [Set upload path](#file_upload_path)

### Separator

- [Basic](#separator_basic)
- [Set text alignment](#separator_align)

### Theming

- [Set initial theme](#theme_basic_noop)
- [Switch theme dynamically](#theme_switching)
- [Dark mode](#theme_dark_mode)
- [Use color variables](#theme_colors)
- [Some sample themes](#theme_samples)

### Advanced Layout

- [An Album](#layout_album)
'''


def view_output(view: View, docs, *args, **kwargs):
    if len(args) == 0:
        # example has no output
        return view(*docs)

    if 'popup' in kwargs:
        # show as-is
        return view(*args, **kwargs)

    # show with docs
    return view(*docs, col(*args, name='output', padding=20, border='$accent', **kwargs))


def main(view: View):
    topic = view(table_of_contents)
    topics[topic](view)


nitro = View(
    main,
    title='Nitro',
    caption=f'v{version}',
    menu=[
        option(main, 'Contents', icon='Documentation'),
        option(main, "Basics", icon="TextDocument", options=[
            option(hello_world, "Hello World!", icon="TextDocument"),
            option(format_content, "Formatting content", icon="TextDocument"),
            option(format_multiline_content, "Show multiline content", icon="TextDocument"),
            option(display_multiple, "Show multiple items", icon="TextDocument"),
            option(sequence_views, "Show multiple items, one at a time", icon="TextDocument"),
            option(style_text, "Style text", icon="TextDocument"),
            option(get_input, "Get user input", icon="TextDocument"),
            option(sequence_inputs, "Get multiple inputs, one at a time", icon="TextDocument"),
            option(accept_multiple_inputs, "Get multiple inputs at once", icon="TextDocument"),
            option(dunk_your_donuts, "Putting it all together", icon="TextDocument"),
        ]),
        option(main, "Markdown", icon="TextDocument", options=[
            option(markdown_basic, "Basics", icon="TextDocument"),
            option(markdown_links, "Handle clicks on links", icon="TextDocument"),
            option(markdown_table, "Show tables", icon="TextDocument"),
            option(show_table, "Create tables from lists", icon="TextDocument"),
            option(markdown_syntax_highlighting, "Syntax highlighting in code blocks", icon="TextDocument"),
        ]),
        option(main, "Styling", icon="TextDocument", options=[
            option(styling_background, "Set background color", icon="TextDocument"),
            option(styling_color, "Set text color", icon="TextDocument"),
            option(styling_border, "Set border color", icon="TextDocument"),
            option(styling_align, "Set text alignment", icon="TextDocument"),
            option(styling_size, "Set width and height", icon="TextDocument"),
            option(styling_margin, "Set margins", icon="TextDocument"),
            option(styling_padding, "Set padding", icon="TextDocument"),
        ]),
        option(main, "Images", icon="TextDocument", options=[
            option(image_basic, "Basic", icon="TextDocument"),
            option(image_resize, "Set width and height", icon="TextDocument"),
            option(image_fit, "Scale and clip images", icon="TextDocument"),
            option(image_background, "Use as background", icon="TextDocument"),
            option(image_background_pattern, "Use as pattern", icon="TextDocument"),
        ]),
        option(main, "Layout", icon="TextDocument", options=[
            option(layout_basic, "Basics", icon="TextDocument"),
            option(layout_row, "Lay out horizontally", icon="TextDocument"),
            option(layout_col, "Lay out vertically", icon="TextDocument"),
            option(layout_tile, "Control tiling", icon="TextDocument"),
            option(layout_cross_tile, "Control cross tiling", icon="TextDocument"),
            option(layout_gap, "Control spacing", icon="TextDocument"),
            option(layout_wrap, "Control wrapping", icon="TextDocument"),
            option(layout_grow_shrink, "Grow or shrink some items", icon="TextDocument"),
            option(layout_vertical_alignment, "Center content vertically", icon="TextDocument"),
        ]),
        option(main, "Forms", icon="TextDocument", options=[
            option(form_basic, "Basic", icon="TextDocument"),
            option(form_horizontal, "Horizontal", icon="TextDocument"),
            option(form_combo, "Combined", icon="TextDocument"),
            option(form_improved, "Improved", icon="TextDocument"),
        ]),
        option(main, "Popups", icon="TextDocument", options=[
            option(popup_basic, "Basic", icon="TextDocument"),
            option(popup_title, "Set popup title", icon="TextDocument"),
            option(popup_buttons, "Customize buttons", icon="TextDocument"),
        ]),
        option(main, "Textbox", icon="TextDocument", options=[
            option(textbox_basic, "Basic", icon="TextDocument"),
            option(textbox_value, "Set initial value", icon="TextDocument"),
            option(textbox_label, "Set a label", icon="TextDocument"),
            option(textbox_placeholder, "Show placeholder text", icon="TextDocument"),
            option(textbox_required, "Mark as required", icon="TextDocument"),
            option(textbox_mask, "Control input format", icon="TextDocument"),
            option(textbox_icon, "Show an icon", icon="TextDocument"),
            option(textbox_prefix, "Set prefix text", icon="TextDocument"),
            option(textbox_suffix, "Set suffix text", icon="TextDocument"),
            option(textbox_prefix_suffix, "Set both prefix and suffix texts", icon="TextDocument"),
            option(textbox_error, "Show an error message", icon="TextDocument"),
            option(textbox_password, "Accept a password", icon="TextDocument"),
            option(textarea, "Enable multiple lines", icon="TextDocument"),
        ]),
        option(main, "Spinbox", icon="TextDocument", options=[
            option(spinbox_basic, "Basic", icon="TextDocument"),
            option(spinbox_value, "Set initial value", icon="TextDocument"),
            option(spinbox_min, "Set min value", icon="TextDocument"),
            option(spinbox_max, "Set max value", icon="TextDocument"),
            option(spinbox_step, "Set step", icon="TextDocument"),
            option(spinbox_precision, "Set precision", icon="TextDocument"),
            option(spinbox_range, "Combine min, max, step, precision", icon="TextDocument"),
            option(spinbox_range_alt, "Set range", icon="TextDocument"),
            option(spinbox_range_alt_step, "Set range with step", icon="TextDocument"),
            option(spinbox_range_alt_precision, "Set range with precision", icon="TextDocument"),
            option(spinbox_negative, "Use zero-crossing ranges", icon="TextDocument"),
            option(spinbox_decimal_step, "Use fractional steps", icon="TextDocument"),
        ]),
        option(main, "Checkbox", icon="TextDocument", options=[
            option(checkbox_basic, "Basic", icon="TextDocument"),
            option(checkbox_value, "Set initial value", icon="TextDocument"),
        ]),
        option(main, "Toggle", icon="TextDocument", options=[
            option(toggle_basic, "Basic", icon="TextDocument"),
        ]),
        option(main, "Pickers", icon="TextDocument", options=[
            option(picker_basic, "Basic", icon="TextDocument"),
            option(picker_buttons, "Show buttons", icon="TextDocument"),
            option(picker_radio, "Show radio buttons", icon="TextDocument"),
            option(picker_dropdown, "Show a dropdown menu", icon="TextDocument"),
            option(picker_multiple_dropdown, "Show a dropdown list", icon="TextDocument"),
            option(picker_checklist, "Show a checklist", icon="TextDocument"),
            option(picker_dropdown_required, "Mark as required", icon="TextDocument"),
            option(picker_dropdown_error, "Show an error message", icon="TextDocument"),
        ]),
        option(main, "Options", icon="TextDocument", options=[
            option(options_basic, "Basic", icon="TextDocument"),
            option(options_sequence, "Create options from a sequence", icon="TextDocument"),
            option(options_string, "Create options from a string", icon="TextDocument"),
            option(options_tuples, "Create options from tuples", icon="TextDocument"),
            option(options_dict, "Create options from a dictionary", icon="TextDocument"),
            option(options_selected, "Mark options as selected", icon="TextDocument"),
            option(options_value, "Set initial selection", icon="TextDocument"),
        ]),
        option(main, "Buttons", icon="TextDocument", options=[
            option(buttons_basic, "Basic", icon="TextDocument"),
            option(buttons_shorthand, "Shorthand notation", icon="TextDocument"),
            option(buttons_selected, "Mark button as primary", icon="TextDocument"),
            option(buttons_value, "Select primary button", icon="TextDocument"),
            option(buttons_values, "Select multiple primary buttons", icon="TextDocument"),
            option(buttons_split, "Add a menu", icon="TextDocument"),
            option(buttons_selected_split, "Add a menu to a primary button", icon="TextDocument"),
            option(buttons_caption, "Set a caption", icon="TextDocument"),
            option(buttons_layout, "Lay out buttons vertically", icon="TextDocument"),
        ]),
        option(main, "Radio Buttons", icon="TextDocument", options=[
            option(radio_basic, "Basic", icon="TextDocument"),
            option(radio_value, "Set initial selection", icon="TextDocument"),
            option(radio_selected, "Mark options as selected", icon="TextDocument"),
            option(radio_icon, "Show pictorial options", icon="TextDocument"),
        ]),
        option(main, "Dropdown", icon="TextDocument", options=[
            option(dropdown_basic, "Basic", icon="TextDocument"),
            option(dropdown_value, "Set initial selection", icon="TextDocument"),
            option(dropdown_selected, "Mark options as selected", icon="TextDocument"),
            option(dropdown_grouped, "Group options", icon="TextDocument"),
            option(dropdown_editable, "Enable arbitrary input", icon="TextDocument"),
        ]),
        option(main, "Dropdown List", icon="TextDocument", options=[
            option(multi_dropdown_basic, "Basic", icon="TextDocument"),
            option(multi_dropdown_value, "Set initial selection", icon="TextDocument"),
            option(multi_dropdown_selected, "Mark options as selected", icon="TextDocument"),
        ]),
        option(main, "Checklist", icon="TextDocument", options=[
            option(checklist_basic, "Basic", icon="TextDocument"),
            option(checklist_value, "Set initial selection", icon="TextDocument"),
            option(checklist_selected, "Mark options as checked", icon="TextDocument"),
        ]),
        option(main, "Table", icon="TextDocument", options=[
            option(table_basic, "Basic", icon="TextDocument"),
            option(table_clickable, "Make rows clickable", icon="TextDocument"),
            option(table_markdown, "Use markdown in cells", icon="TextDocument"),
            option(table_multiselect, "Enable multi-select", icon="TextDocument"),
            option(table_singleselect, "Enable single select", icon="TextDocument"),
            option(table_value, "Set initial selection", icon="TextDocument"),
            option(table_selected, "Mark rows as selected", icon="TextDocument"),
            option(table_grouped, "Group rows", icon="TextDocument"),
            option(table_multilevel, "Group rows at multiple levels", icon="TextDocument"),
            option(table_column_width, "Set column width", icon="TextDocument"),
            option(table_header_icon, "Set header icon", icon="TextDocument"),
            option(table_header_resizable, "Disable column resizing", icon="TextDocument"),
            option(table_column_multiline, "Enable multiline cells", icon="TextDocument"),
        ]),
        option(main, "Slider", icon="TextDocument", options=[
            option(slider_basic, "Basic", icon="TextDocument"),
            option(slider_value, "Set initial value", icon="TextDocument"),
            option(slider_min, "Set min value", icon="TextDocument"),
            option(slider_max, "Set max value", icon="TextDocument"),
            option(slider_step, "Set step", icon="TextDocument"),
            option(slider_precision, "Set precision", icon="TextDocument"),
            option(slider_range, "Combine min, max, step, precision", icon="TextDocument"),
            option(slider_range_alt, "Set range", icon="TextDocument"),
            option(slider_range_alt_step, "Set range with step", icon="TextDocument"),
            option(slider_range_alt_precision, "Set range with precision", icon="TextDocument"),
            option(slider_negative, "Zero-crossing range", icon="TextDocument"),
            option(slider_decimal_step, "Set fractional steps", icon="TextDocument"),
        ]),
        option(main, "Range Slider", icon="TextDocument", options=[
            option(range_slider_basic, "Basic", icon="TextDocument"),
            option(range_slider_min, "Set min value", icon="TextDocument"),
            option(range_slider_max, "Set max value", icon="TextDocument"),
            option(range_slider_step, "Set step", icon="TextDocument"),
            option(range_slider_precision, "Set precision", icon="TextDocument"),
            option(range_slider_range, "Combine min, max, step, precision", icon="TextDocument"),
            option(range_slider_range_alt, "Set range", icon="TextDocument"),
            option(range_slider_range_alt_step, "Set range with step", icon="TextDocument"),
            option(range_slider_range_alt_precision, "Set range with precision", icon="TextDocument"),
            option(range_slider_negative, "Use zero-crossing range", icon="TextDocument"),
            option(range_slider_decimal_step, "Set fractional steps", icon="TextDocument"),
        ]),
        option(main, "Time Picker", icon="TextDocument", options=[
            option(time_basic, "Basic", icon="TextDocument"),
            option(time_seconds, "Enable seconds", icon="TextDocument"),
            option(time_hour, "Show hours only", icon="TextDocument"),
            option(time_24, "Show 24-hour clock", icon="TextDocument"),
            option(time_24_seconds, "Show 24-hour clock, with seconds", icon="TextDocument"),
            option(time_24_hour, "Show 24-hour clock, with hour only", icon="TextDocument"),
        ]),
        option(main, "Date Picker", icon="TextDocument", options=[
            option(date_basic, "Basic", icon="TextDocument"),
            option(date_value, "Set initial date", icon="TextDocument"),
            option(date_placeholder, "Set placeholder text", icon="TextDocument"),
            option(date_min, "Set min date", icon="TextDocument"),
            option(date_max, "Set max date", icon="TextDocument"),
            option(date_min_max, "Combine min and max date", icon="TextDocument"),
            option(date_range, "Set range", icon="TextDocument"),
            option(date_required, "Mark as required", icon="TextDocument"),
        ]),
        option(main, "Calendar", icon="TextDocument", options=[
            option(day_basic, "Basic", icon="TextDocument"),
            option(day_value, "Set initial date", icon="TextDocument"),
            option(day_min, "Set min date", icon="TextDocument"),
            option(day_max, "Set max date", icon="TextDocument"),
            option(day_min_max, "Combine min and max dates", icon="TextDocument"),
            option(day_range, "Set range", icon="TextDocument"),
        ]),
        option(main, "Week Picker", icon="TextDocument", options=[
            option(week_basic, "Basic", icon="TextDocument"),
            option(week_value, "Set initial week", icon="TextDocument"),
            option(week_min, "Set min date", icon="TextDocument"),
            option(week_max, "Set max date", icon="TextDocument"),
            option(week_min_max, "Combine min and max dates", icon="TextDocument"),
            option(week_range, "Set range", icon="TextDocument"),
        ]),
        option(main, "Month Picker", icon="TextDocument", options=[
            option(month_basic, "Basic", icon="TextDocument"),
            option(month_value, "Set initial month", icon="TextDocument"),
            option(month_min, "Set min date", icon="TextDocument"),
            option(month_max, "Set max date", icon="TextDocument"),
            option(month_min_max, "Combine min and max dates", icon="TextDocument"),
            option(month_range, "Set range", icon="TextDocument"),
        ]),
        option(main, "Tag Picker", icon="TextDocument", options=[
            option(tag_picker_basic, "Basic", icon="TextDocument"),
            option(tag_picker_value, "Set initial tags", icon="TextDocument"),
            option(tag_picker_selected, "Mark tags as selected", icon="TextDocument"),
        ]),
        option(main, "Color Picker", icon="TextDocument", options=[
            option(color_basic, "Basic", icon="TextDocument"),
            option(color_value, "Set initial color", icon="TextDocument"),
        ]),
        option(main, "Color Palette", icon="TextDocument", options=[
            option(palette_basic, "Basic", icon="TextDocument"),
            option(palette_value, "Set initial color", icon="TextDocument"),
            option(palette_selected, "Mark colors as selected", icon="TextDocument"),
        ]),
        option(main, "Rating", icon="TextDocument", options=[
            option(rating_basic, "Basic", icon="TextDocument"),
            option(rating_value, "Set initial rating", icon="TextDocument"),
            option(rating_min, "Allow zero stars", icon="TextDocument"),
            option(rating_max, "Set maximum number of stars", icon="TextDocument"),
            option(rating_min_max, "Combine min and max stars", icon="TextDocument"),
            option(rating_range, "Set range", icon="TextDocument"),
        ]),
        option(main, "File Upload", icon="TextDocument", options=[
            option(file_upload_basic, "Basic", icon="TextDocument"),
            option(file_upload_multiple, "Allow multiple files", icon="TextDocument"),
            option(file_upload_path, "Set upload path", icon="TextDocument"),
        ]),
        option(main, "Separator", icon="TextDocument", options=[
            option(separator_basic, "Basic", icon="TextDocument"),
            option(separator_align, "Set text alignment", icon="TextDocument"),
        ]),
        option(main, "Theming", icon="TextDocument", options=[
            option(theme_basic_noop, "Set initial theme", icon="TextDocument"),
            option(theme_switching, "Switch theme dynamically", icon="TextDocument"),
            option(theme_dark_mode, "Dark mode", icon="TextDocument"),
            option(theme_colors, "Use color variables", icon="TextDocument"),
            option(theme_samples, "Some sample themes", icon="TextDocument"),
        ]),
        option(main, "Advanced Layout", icon="TextDocument", options=[
            option(layout_album, "An Album", icon="TextDocument"),
        ]),
    ],
    nav=[
        option(main, 'Contents', name='contents'),
    ],
)

app = Flask(__name__, static_folder=web_directory, static_url_path='')
UPLOAD_DIR = './file_uploads'
Path(UPLOAD_DIR).mkdir(exist_ok=True)


@app.route('/')
def home_page():
    return send_from_directory(web_directory, 'index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Missing files part', 400
    files = request.files.getlist('file')
    filenames = []
    for file in files:
        if file.filename == '':
            return 'Empty file', 400
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_DIR, filename))
            filenames.append(filename)
    return json.dumps(dict(files=filenames))


@app.route('/nitro', websocket=True)
def socket():
    ws = simple_websocket.Server(request.environ)
    try:
        nitro.serve(ws.send, ws.receive)
    except simple_websocket.ConnectionClosed:
        pass
    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4999)
