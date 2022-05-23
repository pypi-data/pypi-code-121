'''
Tests for StoneMark
'''

from __future__ import unicode_literals

from . import PPLCStream
from . import *
from textwrap import dedent
from unittest import TestCase, main


class TestCase(TestCase):

    def __init__(self, *args, **kwds):
        regex = getattr(self, 'assertRaisesRegex', None)
        if regex is None:
            self.assertRaisesRegex = getattr(self, 'assertRaisesRegexp')
        super(TestCase, self).__init__(*args, **kwds)


class TestPPLCStream(TestCase):

    def test_get_char(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        result = []
        line_no = 0
        while stream:
            self.assertEqual(stream.line_no, line_no)
            ch = stream.get_char()
            result.append(ch)
            if ch == '\n':
                line_no += 1
        self.assertEqual(''.join(result), sample+'\n')
        self.assertEqual(line_no, 2)
        self.assertEqual(line_no, stream.line_no)

    def test_get_line(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        result = []
        line_no = 0
        while stream:
            self.assertEqual(stream.line_no, line_no)
            line = stream.get_line()
            result.append(line)
            line_no += 1
        self.assertEqual(''.join(result), sample+'\n')
        self.assertEqual(line_no, 2)
        self.assertEqual(line_no, stream.line_no)

    def test_peek_line(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        self.assertEqual(stream.current_line, 'line one\n')
        self.assertEqual(stream.peek_line(), 'line two\n')
        self.assertEqual(stream.get_line(), 'line one\n')
        self.assertEqual(stream.current_line, 'line two\n')
        self.assertEqual(stream.peek_line(), '')
        self.assertEqual(stream.get_line(), 'line two\n')
        self.assertEqual(stream.current_line, '')
        try:
            stream.get_line()
        except EOFError:
            pass

    def test_push_char(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        result = []
        stream.push_char('2')
        stream.push_char('4')
        line_no = 0
        while stream:
            self.assertEqual( stream.line_no, line_no)
            line = stream.get_line()
            result.append(line)
            line_no += 1
        self.assertEqual( ''.join(result), '42'+sample+'\n')
        self.assertEqual( line_no, 2)
        self.assertEqual( line_no, stream.line_no)

    def test_push_line(self):
        sample = u'line one\nline two'
        stream = PPLCStream(sample)
        result = []
        stream.push_line('line zero')
        line_no = 0
        while stream:
            self.assertEqual( stream.line_no, line_no)
            ch = stream.get_char()
            result.append(ch)
            if ch == '\n':
                line_no += 1
        self.assertEqual( ''.join(result), 'line zero\n'+sample+'\n')
        self.assertEqual( line_no, 3)
        self.assertEqual( line_no, stream.line_no)


class TestStonemark(TestCase):
    def test_simple_doc_1(self):
        test_doc = dedent("""\
        ==============
        Document Title
        ==============

        In this paragraph we see that we have multiple lines of a single
        sentence.

        - plus a two-line
        - list for good measure
          + and a sublist
          + for really good measure

        Now a tiny paragraph.

            and a code block!

        ```
        and another code block!
        ```
        """)

        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading,  Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem, ]]], Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <p>Now a tiny paragraph.</p>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_2(self):
        test_doc = dedent("""\
                ==============
                Document Title
                ==============

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  1) and a sublist
                  2) for really good measure
                - back to main list


                ```
                and another code block!
                ```
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]], ListItem], CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ol>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ol>
                <li>back to main list</li>
                </ul>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_3(self):
        test_doc = dedent("""\
                Document Title
                ==============

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  + and a sublist
                  + for really good measure

                Now a tiny paragraph I mean header
                ----------------------------------

                    and a code block!

                ```
                and another code block!
                ```
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Heading, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h2>Document Title</h2>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <h3>Now a tiny paragraph I mean header</h3>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_4(self):
        test_doc = dedent("""\
                Document Title
                ==============

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  + and a sublist
                  + for really good measure

                Now a tiny paragraph I mean header
                ----------------------------------

                    and a code block!

                ```
                and another code block!
                ```
                """)
        doc = Document(test_doc, first_header_is_title=True)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Heading, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <h3>Now a tiny paragraph I mean header</h3>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_5(self):
        test_doc = dedent("""\
                Document Title
                --------------

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  + and a sublist
                  + for really good measure

                Now a tiny paragraph I mean header
                ----------------------------------

                    and a code block!

                ```
                and another code block!
                ```
                """)
        doc = Document(test_doc, first_header_is_title=True)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Heading, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <h3>Now a tiny paragraph I mean header</h3>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_simple_doc_6(self):
        test_doc = dedent("""\
                Document Title
                --------------

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure

                ---

                Now a tiny paragraph.

                    and a code block!

                ```
                and another code block!
                ```
                """)

        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem], Rule, Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h3>Document Title</h3>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                </ul>

                <hr>

                <p>Now a tiny paragraph.</p>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_failure_1(self):
        test_doc = dedent("""\
                Document Title
                ==============

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  + and a sublist
                  + for really good measure
                - back to main list

                    and a code block!

                ```
                and another code block!
                ```
                """)

        with self.assertRaisesRegex(BadFormat, 'indented code blocks cannot follow lists .line 12.'):
            doc = Document(test_doc)

    def test_format_nesting_1(self):
        test_doc = dedent("""\
                **this is **really important** important info**
                """)
        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), "<p><b>this is really important important info</b></p>")

    def test_format_nesting_2(self):
        test_doc = dedent("""\
                **this is *really important* important info**
                """)
        doc = Document(test_doc)
        self.assertEqual( doc.to_html(), "<p><b>this is <i>really important</i> important info</b></p>")

    def test_format_footnote(self):
        self.maxDiff = None
        test_doc = dedent("""\
                This is a paragraph talking about many things. [^1] The question is:
                how are those many things related?

                ---

                [^1]: Okay, maybe just the one thing.
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph, Rule, IDLink])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about many things.<sup><a href="#footnote-1">[1]</a></sup> The question is:
                how are those many things related?</p>

                <hr>

                <div id="footnote-1"><table><tr><td style="vertical-align: top"><sup>1</sup></td><td>Okay, maybe just the one thing.</td></tr></table></div>
                """).strip())

    def test_format_external_link_1(self):
        test_doc = dedent("""\
                This is a paragraph talking about [board game resources][1].  How many of them
                are there, anyway?

                [1]: http://www.boardgamegeek.com
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">board game resources</a>.  How many of them
                are there, anyway?</p>
                """).strip())

    def test_format_external_link_2(self):
        test_doc = dedent("""\
                This is a paragraph talking about [board game resources](http://www.boardgamegeek.com).  How many of them
                are there, anyway?
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>This is a paragraph talking about <a href="http://www.boardgamegeek.com">board game resources</a>.  How many of them
                are there, anyway?</p>
                """).strip())

    def test_format_wiki_link(self):
        test_doc = dedent("""\
                Check the [Documentation] for more details.
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>Check the <a href="Documentation">Documentation</a> for more details.</p>
                """).strip())


    def test_format_image(self):
        test_doc = dedent("""\
                An introductory paragraph.

                ![*a riveting picture*](https://www.image_library/photos/rivets.png)

                A concluding paragraph.
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc), [Paragraph, Image, Paragraph])
        self.assertEqual( doc.to_html(), dedent("""\
                <p>An introductory paragraph.</p>

                <img src="https://www.image_library/photos/rivets.png" alt="<i>a riveting picture</i>">

                <p>A concluding paragraph.</p>
                """).strip())

    def test_formatted_doc_1(self):
        test_doc = dedent("""\
                ==============
                Document Title
                ==============

                In **this paragraph** we see that we have multiple lines of a *single
                sentence*.

                - plus a ***two-line***
                - list `for good` measure
                  + and __a sublist__
                  + for ~~really~~ good measure

                Now a ==tiny paragraph== that talks about water (H~2~O) raised 2^4^ power.

                    and a code block!

                ```
                and another code block!
                ```
                """)
        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading, Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem]]], Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1>Document Title</h1>

                <p>In <b>this paragraph</b> we see that we have multiple lines of a <i>single
                sentence</i>.</p>

                <ul>
                <li>plus a <b><i>two-line</i></b></li>
                <li>list <code>for good</code> measure</li>
                    <ul>
                    <li>and <u>a sublist</u></li>
                    <li>for <del>really</del> good measure</li>
                    </ul>
                </ul>

                <p>Now a <mark>tiny paragraph</mark> that talks about water (H<sub>2</sub>O) raised 2<sup>4</sup> power.</p>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_html_chars(self):
        self.maxDiff = None
        test_doc = dedent("""\
                ===================
                Some Maths & Stuffs
                ===================

                1) a = 4
                2) b < 5
                3) c > 1

                To ~~everyone~~ *anyone* **who <hears> this** -- HELP![^jk]

                ```
                a < b >= c
                ```

                Is a < b ?  Yes.

                Is a >= b ?  Yes.

                Is a & b = a ?  Yes.

                ![someone sayd, "OReily?"](https://www.fake.com/images/123.png)

                ---

                [^jk]: Just a joke!  I'm >fine<!
                """)
        doc = Document(test_doc)
        self.assertEqual(
                doc.to_html(),
                dedent("""\
                <h1>Some Maths &amp; Stuffs</h1>

                <ol>
                <li>a = 4</li>
                <li>b &lt; 5</li>
                <li>c &gt; 1</li>
                </ol>

                <p>To <del>everyone</del> <i>anyone</i> <b>who &lt;hears&gt; this</b> -- HELP!<sup><a href="#footnote-jk">[jk]</a></sup></p>

                <pre><code>a &lt; b &gt;= c</code></pre>

                <p>Is a &lt; b ?  Yes.</p>

                <p>Is a &gt;= b ?  Yes.</p>

                <p>Is a &amp; b = a ?  Yes.</p>

                <img src="https://www.fake.com/images/123.png" alt="someone sayd, &quot;OReily?&quot;">

                <hr>

                <div id="footnote-jk"><table><tr><td style="vertical-align: top"><sup>jk</sup></td><td>Just a joke!  I&apos;m &gt;fine&lt;!</td></tr></table></div>
                """).strip(), doc.to_html())

    def test_footnote_children(self):
        self.maxDiff = None
        test_doc = dedent("""\
                Step 1: Build your server
                =========================

                Either include the `OpenSSH` and `Postgres` packages when creating the server, or run the
                following commands after the server is operational [^1]:

                ``` sh
                apt-get install openssh-server postgresql-9.1
                # optional: denyhosts
                ```

                Now make sure your server has all the latest versions & patches by doing an update [^2]:

                ``` sh
                apt-get update
                apt-get dist-upgrade
                ```

                Although not always essential it's probably a good idea to reboot your server now and make
                sure it all comes back up and you can login via `ssh`.

                Now we're ready to start the OpenERP install.

                ----

                [^1]: Creating the server, whether with dedicated hardware or as a virtual machine, is not
                      covered by these instructions.

                [^2]: If the `update` command results in `failed to fetch` errors, you can try these commands:

                      ```
                      rm -rf /var/lib/apt/lists/*
                      apt-get clean
                      apt-get update
                      ```

                      And try the `update` command again.  If you are now having missing key errors, try:

                      ```sh
                      gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv <MISSING_KEY>
                      ```

                      Then try the `update` command one more time.

                      When `update` works correctly (no errors) run the `dist-upgrade` command.

                ----

                [Next](oe-install-step-2)
                """)
        expected = dedent("""\
                <h2>Step 1: Build your server</h2>

                <p>Either include the <code>OpenSSH</code> and <code>Postgres</code> packages when creating the server, or run the
                following commands after the server is operational<sup><a href="#footnote-1">[1]</a></sup>:</p>

                <pre><code>apt-get install openssh-server postgresql-9.1
                # optional: denyhosts</code></pre>

                <p>Now make sure your server has all the latest versions &amp; patches by doing an update<sup><a href="#footnote-2">[2]</a></sup>:</p>

                <pre><code>apt-get update
                apt-get dist-upgrade</code></pre>

                <p>Although not always essential it&apos;s probably a good idea to reboot your server now and make
                sure it all comes back up and you can login via <code>ssh</code>.</p>

                <p>Now we&apos;re ready to start the OpenERP install.</p>

                <hr>

                <div id="footnote-1"><table><tr><td style="vertical-align: top"><sup>1</sup></td><td>Creating the server, whether with dedicated hardware or as a virtual machine, is not
                covered by these instructions.</td></tr></table></div>

                <div id="footnote-2"><table><tr><td style="vertical-align: top"><sup>2</sup></td><td>If the <code>update</code> command results in <code>failed to fetch</code> errors, you can try these commands:

                <pre><code>rm -rf /var/lib/apt/lists/*
                apt-get clean
                apt-get update</code></pre>

                <p>And try the <code>update</code> command again.  If you are now having missing key errors, try:</p>

                <pre><code>gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv &lt;MISSING_KEY&gt;</code></pre>

                <p>Then try the <code>update</code> command one more time.</p>

                <p>When <code>update</code> works correctly (no errors) run the <code>dist-upgrade</code> command.</p></td></tr></table></div>

                <hr>

                <p><a href="oe-install-step-2">Next</a></p>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_optional_blank_lines(self):
        self.maxDiff = None
        test_doc = dedent("""\
                ===================
                Pulse Specification
                ===================

                Tracking
                ========

                - frequency
                  - daily
                  - weekly
                  - monthly
                  - yearly

                - status
                  - pass/fail
                  - percentage
                  - text
                  - tripline

                - device/job
                  - 11.16/sync
                  - 11.111/backup""")
        expected = dedent("""\
                <h1>Pulse Specification</h1>

                <h2>Tracking</h2>

                <ul>
                <li>frequency</li>
                    <ul>
                    <li>daily</li>
                    <li>weekly</li>
                    <li>monthly</li>
                    <li>yearly</li>
                    </ul>
                <li>status</li>
                    <ul>
                    <li>pass/fail</li>
                    <li>percentage</li>
                    <li>text</li>
                    <li>tripline</li>
                    </ul>
                <li>device/job</li>
                    <ul>
                    <li>11.16/sync</li>
                    <li>11.111/backup</li>
                    </ul>
                </ul>""").strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_code_with_footnote(self):
        test_doc = dedent("""\
                Here is `some code`[^hah].

                [^hah]: and a footnote
                """)
        expected = dedent("""\
                <p>Here is <code>some code</code><sup><a href="#footnote-hah">[hah]</a></sup>.</p>

                <div id="footnote-hah"><table><tr><td style="vertical-align: top"><sup>hah</sup></td><td>and a footnote</td></tr></table></div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_duplicate_footnote(self):
        test_doc = dedent("""\
                Here is `some code`[^hah].

                And then another [^hah].

                [^hah]: and a footnote
                """)
        expected = dedent("""\
                <p>Here is <code>some code</code><sup><a href="#footnote-hah">[hah]</a></sup>.</p>

                <p>And then another<sup><a href="#footnote-hah">[hah]</a></sup>.</p>

                <div id="footnote-hah"><table><tr><td style="vertical-align: top"><sup>hah</sup></td><td>and a footnote</td></tr></table></div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_parens(self):
        test_doc = dedent("""\
                Here is (a parenthetical)[^hah].

                [^hah]: and a footnote
                """)
        expected = dedent("""\
                <p>Here is (a parenthetical)<sup><a href="#footnote-hah">[hah]</a></sup>.</p>

                <div id="footnote-hah"><table><tr><td style="vertical-align: top"><sup>hah</sup></td><td>and a footnote</td></tr></table></div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_parens_in_code(self):
        test_doc = dedent("""\
                Helper for inserting `Enum` members into a namespace (usually `globals()`).
                """)
        expected = dedent("""\
                <p>Helper for inserting <code>Enum</code> members into a namespace (usually <code>globals()</code>).</p>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_editorial_comment(self):
        test_doc = dedent("""\
                Here is [[editor: wow]][^hah].

                [^hah]: and a footnote
                """)
        expected = dedent("""\
                <p>Here is [editor: wow]<sup><a href="#footnote-hah">[hah]</a></sup>.</p>

                <div id="footnote-hah"><table><tr><td style="vertical-align: top"><sup>hah</sup></td><td>and a footnote</td></tr></table></div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_code_after_link(self):
        test_doc = dedent("""\
                [^1] `some code` and 

                [wiki_page] `204` is the `No Content` status code, and indicates success.

                [^1]: blah
                """)
        expected = dedent("""\
                <p><sup><a href="#footnote-1">[1]</a></sup> <code>some code</code> and</p>

                <p><a href="wiki_page">wiki_page</a> <code>204</code> is the <code>No Content</code> status code, and indicates success.</p>

                <div id="footnote-1"><table><tr><td style="vertical-align: top"><sup>1</sup></td><td>blah</td></tr></table></div>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)

    def test_indented_list(self):
        self.maxDiff = None
        test_doc = dedent("""\
                An OpenERP cron job will monitor the above directory and update the appropriate tables with the information found
                in the message files.  Another OpenERP cron job will check for missing entries, and change the status of the IP
                device to `FIX` if sufficient time has passed:

                  - daily jobs have a grace period of two physical days
                  - weekly and monthly jobs have a grace period of two business days
                  - quarterly and yearly jobs have a grace period of five business days

                Besides the standard frequencies, there are two one-time frequencies:  `trip` and `alert`.  Both indicate an urgent
                issue -- the difference is that `alert` will also cause text messages and email to be sent.
                """)
        expected = dedent("""\
                <p>An OpenERP cron job will monitor the above directory and update the appropriate tables with the information found
                in the message files.  Another OpenERP cron job will check for missing entries, and change the status of the IP
                device to <code>FIX</code> if sufficient time has passed:</p>

                <ul>
                <li>daily jobs have a grace period of two physical days</li>
                <li>weekly and monthly jobs have a grace period of two business days</li>
                <li>quarterly and yearly jobs have a grace period of five business days</li>
                </ul>

                <p>Besides the standard frequencies, there are two one-time frequencies:  <code>trip</code> and <code>alert</code>.  Both indicate an urgent
                issue -- the difference is that <code>alert</code> will also cause text messages and email to be sent.</p>
                """).strip()
        self.assertEqual(Document(test_doc).to_html(), expected)


    def test_coded_headers(self):
        test_doc = dedent("""\
                ================
                `Document Title`
                ================

                In this paragraph we see that we have multiple lines of a single
                sentence.

                - plus a two-line
                - list for good measure
                  + and a sublist
                  + for really good measure

                `stuff`
                -------

                Now a tiny paragraph.

                    and a code block!

                ```
                and another code block!
                ```
                """)

        doc = Document(test_doc)
        self.assertEqual( shape(doc.nodes), [Heading,  Paragraph, List, [ListItem, ListItem, [List, [ListItem, ListItem, ]]], Heading, Paragraph, CodeBlock, CodeBlock])
        self.assertEqual( doc.to_html(), dedent("""\
                <h1><code>Document Title</code></h1>

                <p>In this paragraph we see that we have multiple lines of a single
                sentence.</p>

                <ul>
                <li>plus a two-line</li>
                <li>list for good measure</li>
                    <ul>
                    <li>and a sublist</li>
                    <li>for really good measure</li>
                    </ul>
                </ul>

                <h3><code>stuff</code></h3>

                <p>Now a tiny paragraph.</p>

                <pre><code>and a code block!</code></pre>

                <pre><code>and another code block!</code></pre>
                """).strip())

    def test_not_html_headers(self):
        test_doc = dedent("""\
                =========
                Why X < Y
                =========

                a bunch of stuff
                """)

        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <h1>Why X &lt; Y</h1>

                <p>a bunch of stuff</p>
                """).strip())

    def test_header_sizes(self):
        test_doc = dedent("""\
                =========
                Why X < Y
                =========

                a bunch of stuff

                Summary
                =======

                blah blah

                Notes
                -----

                more blah
                """)

        doc = Document(test_doc, header_sizes=(2,4,5))
        self.assertEqual(doc.to_html(), dedent("""\
                <h2>Why X &lt; Y</h2>

                <p>a bunch of stuff</p>

                <h4>Summary</h4>

                <p>blah blah</p>

                <h5>Notes</h5>

                <p>more blah</p>
                """).strip())


    def test_quotation_1(self):
        test_doc = dedent("""\
                > single level quote

                > level 1 and
                >> level 2
                > level 1 again
                """)
        doc = Document(test_doc, header_sizes=(2,4,5))
        self.assertEqual(doc.to_html(), dedent("""\
                <blockquote>
                            <p>single level quote</p>
                </blockquote>

                <blockquote>
                            <p>level 1 and</p>
                            <blockquote>
                                        <p>level 2</p>
                            </blockquote>
                            <p>level 1 again</p>
                </blockquote>
                """).strip(),
                doc.to_html(),
                )

    def test_quotation_2(self):
        test_doc = dedent("""\
                >>> third level quote
                >>> still third
                >> second
                > first

                > level 1 and
                >> level 2
                > level 1 again
                """)
        doc = Document(test_doc, header_sizes=(2,4,5))
        self.assertEqual(doc.to_html(), dedent("""\
                <blockquote>
                            <blockquote>
                                        <blockquote>
                                                    <p>third level quote
                                                    still third</p>
                                        </blockquote>
                                        <p>second</p>
                            </blockquote>
                            <p>first</p>
                </blockquote>

                <blockquote>
                            <p>level 1 and</p>
                            <blockquote>
                                        <p>level 2</p>
                            </blockquote>
                            <p>level 1 again</p>
                </blockquote>
                """).strip(),
                doc.to_html(),
                )

    def test_quotation_3(self):
        test_doc = dedent("""\
                > A Title
                > =======
                >
                > Then some text, followed by
                >
                > - list item 1
                > - list item 2
                >
                > ``` python
                > and some code
                > ```
                >> another quote block
                > and done

                so there.
                """)
        doc = Document(test_doc)
        self.assertEqual(doc.to_html(), dedent("""\
                <blockquote>
                            <h2>A Title</h2>
                            <p>Then some text, followed by</p>
                            <ul>
                            <li>list item 1</li>
                            <li>list item 2</li>
                            </ul>
                            <pre><code>and some code</code></pre>
                            <blockquote>
                                        <p>another quote block</p>
                            </blockquote>
                            <p>and done</p>
                </blockquote>

                <p>so there.</p>
                """).strip(),
                doc.to_html(),
                )



def shape(document, text=False):
    result = []
    if isinstance(document, Document):
        document = document.nodes
    for thing in document:
        if not text and isinstance(thing, Text):
            continue
        elif isinstance(thing, Node):
            result.append(thing.__class__)
            intermediate = shape(thing.items)
            if intermediate:
                result.append(intermediate)
    return result

main()
