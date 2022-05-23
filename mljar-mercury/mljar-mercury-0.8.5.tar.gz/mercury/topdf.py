#!/usr/bin/env python
import asyncio
import os
import tempfile

from pyppeteer import launch

import concurrent.futures

async def html_to_pdf(html_file, pdf_file, pyppeteer_args=None):
    """Convert a HTML file to a PDF"""
    browser = await launch(
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False,
        args=pyppeteer_args or [],
    )
    page = await browser.newPage()
    await page.setViewport(dict(width=994, height=768))
    await page.emulateMedia("screen")

    await page.goto(f"file:///home/piotr/sandbox/mercury/mercury/{html_file}", {"waitUntil": ["networkidle2"]})

    page_margins = {
        "left": "20px",
        "right": "20px",
        "top": "30px",
        "bottom": "30px",
    }

    dimensions = await page.evaluate(
        """() => {
        return {
            width: document.body.scrollWidth,
            height: document.body.scrollHeight,
            offsetWidth: document.body.offsetWidth,
            offsetHeight: document.body.offsetHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }"""
    )
    width = dimensions["width"]
    height = dimensions["height"]

    await page.evaluate(
        """
    function getOffset( el ) {
        var _x = 0;
        var _y = 0;
        while( el && !isNaN( el.offsetLeft ) && !isNaN( el.offsetTop ) ) {
            _x += el.offsetLeft - el.scrollLeft;
            _y += el.offsetTop - el.scrollTop;
            el = el.offsetParent;
        }
        return { top: _y, left: _x };
        }
    """,
        force_expr=True,
    )

    await page.addStyleTag(
        {
            "content": """
                #notebook-container {
                    box-shadow: none;
                    padding: unset
                }
                div.cell {
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                div.output_wrapper {
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                div.output {
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                /* Jupyterlab based HTML uses these classes */
                .jp-Cell-inputWrapper {
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                .jp-Cell-outputWrapper {
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                .jp-Notebook {
                    margin: 0px;
                }
                /* Hide the message box used by MathJax */
                #MathJax_Message {
                    display: none;
                }
         """
        }
    )

    await page.pdf(
        {
            "path": pdf_file,
            # Adobe can not display pages longer than 200inches. So we limit
            # ourselves to that and start a new page if needed.
            #"width": min(width + 2, 200 * 72),
            #"height": min(height + 2, 200 * 72),
            "format": "A4",
            "printBackground": True,
            "margin": page_margins,
        }
    )

    headings = await page.evaluate(
        """() => {
        var vals = []
        for (const elem of document.getElementsByTagName("h1")) {
            vals.push({ top: getOffset(elem).top * (1-72/288), text: elem.innerText })
        }
        for (const elem of document.getElementsByTagName("h2")) {
            vals.push({ top: getOffset(elem).top * (1-72/288), text: "∙ " + elem.innerText })
        }
        return vals
    }"""
    )

    await browser.close()

    return headings


def main():
    print("topdf")
    pool = concurrent.futures.ThreadPoolExecutor()
    pyppeteer_args = []
    heading_positions = pool.submit(
                asyncio.run,
                html_to_pdf(
                    "slides2.slides.html?print-pdf", "slides-my.pdf", pyppeteer_args=pyppeteer_args,
                ),
            ).result()
    print(heading_positions)

if __name__ == "__main__":
    main()
