from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Union

from dominate import document
from dominate.tags import a, div, h1, h2, img, p
from dominate.util import raw

from ..rex import grouped_impacts_table

CSS = r"""
<style>
html {
  max-width: 100ch;
  padding: 2rem;
  margin: auto;
}
body {
  font-family: Liberation Sans, Arial, sans-serif;
  background-color: #fffaf7;
  line-height: 1.5;
}
header {
  margin-bottom: 1.5rem;
}
h1 {
  margin-bottom: .5rem;
}
pre {
  white-space: pre-wrap;
}
hr {
  margin-top: 2rem;
}
.marginauto {
  margin-left: auto;
  margin-right: auto;
  width: 60%;
}
</style>
"""


def fig(v, r, s, t) -> Path:
    return f"matplotlib/VRP_reg{r}_{v}_{s}Fit.{t}"


def add_images(d, vs, r, s, t=None):
    if t is not None:
        d.add(p(t))
    for v in vs:
        d.add(a(img(src=fig(v, r, s, "png"), width="250px"), href=fig(v, r, s, "pdf")))


def index_dot_html(rex_dir: str | Path) -> None:
    rex_dir = Path(rex_dir)
    doc = document(title="tW Fit")
    with doc.head:
        raw(CSS)

    mpl_dir = rex_dir / "matplotlib"
    if not mpl_dir.exists():
        subprocess.Popen(
            f"tdub rex stacks --no-chisq --no-internal --png {rex_dir}", shell=True
        ).wait()
        subprocess.Popen(
            f"python3 -m tdub.internal.cramped {rex_dir}", shell=True
        ).wait()

    img_pairs = []
    for entry in mpl_dir.glob("*.png"):
        if "VRP" in entry.stem:
            pair = (mpl_dir / f"{entry.stem}.pdf", mpl_dir / f"{entry.stem}.png")
            img_pairs.append(pair)

    allrs_png_pair = ("matplotlib/allregions_pre.png", "matplotlib/allregions_post.png")
    r1j1b_png_pair = ("matplotlib/reg1j1b_preFit.png", "matplotlib/reg1j1b_postFit.png")
    r2j1b_png_pair = ("matplotlib/reg2j1b_preFit.png", "matplotlib/reg2j1b_postFit.png")
    r2j2b_png_pair = ("matplotlib/reg2j2b_preFit.png", "matplotlib/reg2j2b_postFit.png")
    allrs_pdf_pair = ("matplotlib/allregions_pre.pdf", "matplotlib/allregions_post.pdf")
    r1j1b_pdf_pair = ("matplotlib/reg1j1b_preFit.pdf", "matplotlib/reg1j1b_postFit.pdf")
    r2j1b_pdf_pair = ("matplotlib/reg2j1b_preFit.pdf", "matplotlib/reg2j1b_postFit.pdf")
    r2j2b_pdf_pair = ("matplotlib/reg2j2b_preFit.pdf", "matplotlib/reg2j2b_postFit.pdf")

    with doc:
        h1("Latest tW Fit")
        p("Generated {}".format(datetime.now().strftime("%b-%d-%Y %H:%M:%S")))
        with p():
            a("INT note link", href="https://cds.cern.ch/record/2667560")
        h2("Main Plots")
        p("Click images for PDF versions.")
        p("Prefit individuals")
        with div(cls="row"):
            with a(href=str(r1j1b_pdf_pair[0])):
                img(src=str(r1j1b_png_pair[0]), width=r"250px")
            with a(href=str(r2j1b_pdf_pair[0])):
                img(src=str(r2j1b_png_pair[0]), width=r"250px")
            with a(href=str(r2j2b_pdf_pair[0])):
                img(src=str(r2j2b_png_pair[0]), width=r"250px")
        p("Prefit combined")
        with div(cls="row"):
            with a(href=str(allrs_pdf_pair[0])):
                img(src=str(allrs_png_pair[0]), cls="marginauto")
        p("Postfit individuals")
        with div(cls="row"):
            with a(href=str(r1j1b_pdf_pair[1])):
                img(src=str(r1j1b_png_pair[1]), width=r"250px")
            with a(href=str(r2j1b_pdf_pair[1])):
                img(src=str(r2j1b_png_pair[1]), width=r"250px")
            with a(href=str(r2j2b_pdf_pair[1])):
                img(src=str(r2j2b_png_pair[1]), width=r"250px")
        p("Postfit combined")
        with div(cls="row"):
            with a(href=str(allrs_pdf_pair[1])):
                img(src=str(allrs_png_pair[1]), cls="marginauto")

        h2("Grouped Uncertainty Impacts (alphabetical then descending)")
        with div():
            p(raw(grouped_impacts_table(rex_dir, descending=False, tablefmt="html")))
            p(raw(grouped_impacts_table(rex_dir, descending=True, tablefmt="html")))

        h2("Other Plots 1j1b")
        with div() as d:
            add_images(
                d,
                ["pT_lep1", "pT_lep2", "pT_jet1", "met"],
                "1j1b",
                "pre",
                t="1j1b pre-fit kinematics",
            )
            add_images(
                d,
                ["pT_lep1", "pT_lep2", "pT_jet1", "met"],
                "1j1b",
                "post",
                t="1j1b post-fit kinematics",
            )
            add_images(
                d,
                ["pTsys_lep1lep2jet1met", "pT_jetS1", "cent_lep1lep2"],
                "1j1b",
                "pre",
                t="Top 3 1j1b BDT inputs pre-fit",
            )
            add_images(
                d,
                ["pTsys_lep1lep2jet1met", "pT_jetS1", "cent_lep1lep2"],
                "1j1b",
                "post",
                t="Top 3 1j1b BDT inputs post-fit",
            )

        h2("Other Plots 2j1b")
        with div() as d:
            add_images(
                d, ["pT_lep1", "pT_lep2"], "2j1b", "pre", t="2j1b pre-fit kinematics"
            )
            add_images(d, ["pT_jet1", "pT_jet2", "met"], "2j1b", "pre")

            add_images(
                d, ["pT_lep1", "pT_lep2"], "2j1b", "post", t="2j1b post-fit kinematics"
            )
            add_images(d, ["pT_jet1", "pT_jet2", "met"], "2j1b", "post")

            add_images(
                d,
                ["mass_lep1jet2", "mass_lep1jet1", "pTsys_lep1lep2jet1met"],
                "2j1b",
                "pre",
                t="Top 3 2j1b BDT inputs pre-fit",
            )
            add_images(
                d,
                ["mass_lep1jet2", "mass_lep1jet1", "pTsys_lep1lep2jet1met"],
                "2j1b",
                "post",
                t="Top 3 2j1b BDT inputs post-fit",
            )

        h2("other Plots 2j2b")
        with div() as d:
            add_images(
                d, ["pT_lep1", "pT_lep2"], "2j2b", "pre", t="2j2b pre-fit kinematics"
            )
            add_images(d, ["pT_jet1", "pT_jet2", "met"], "2j2b", "pre")
            add_images(
                d, ["pT_lep1", "pT_lep2"], "2j2b", "post", t="2j2b post-fit kinematics"
            )
            add_images(d, ["pT_jet1", "pT_jet2", "met"], "2j2b", "post")

            add_images(
                d,
                ["mass_lep1jet1", "mass_lep1jet2", "pT_jet2"],
                "2j2b",
                "pre",
                t="Top 3 2j2b BDT inputs pre-fit",
            )
            add_images(
                d,
                ["mass_lep1jet1", "mass_lep1jet2", "pT_jet2"],
                "2j2b",
                "post",
                t="Top 3 2j2b BDT inputs post-fit",
            )

    with open(Path(rex_dir) / "index.html", "w") as f:
        print(doc, file=f)
