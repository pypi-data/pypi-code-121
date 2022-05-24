#!/usr/bin/env python
"""Download datasets from shareloc.xyz website.
"""

import os
import yaml
import fnmatch
import urllib.request
from urllib.parse import urljoin
import tempfile
import shutil

from tqdm import tqdm
from shareloc_utils.smlm_file import read_smlm_file


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_path):
    with DownloadProgressBar(
        unit="B", unit_scale=True, miniters=1, desc=url.split("/")[-1]
    ) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


def resolve_url(rdf_url, path):
    return urljoin(os.path.dirname(rdf_url) + "/", path)


def convert_smlm(file_path, delimiter=",", extension=".csv"):
    smlm_info = read_smlm_file(file_path)
    for file_info in smlm_info["files"]:
        cols = file_info["cols"]
        rows = file_info["rows"]
        headers = file_info["headers"]
        table = file_info["data"]
        with open(file_path.replace(".smlm", extension), "w") as f:
            for i in range(cols):
                f.write(headers[i] + (delimiter if i < cols - 1 else "\n"))
            for i in tqdm(range(rows), total=rows):
                for j in range(cols):
                    f.write(
                        f"{table[headers[j]][i]:.3f}"
                        + (delimiter if j < cols - 1 else "\n")
                    )


def convert_potree(file_path, zip):
    import pypotree
    import numpy as np

    manifest = read_smlm_file(file_path)
    tables = manifest["files"]
    table = tables[0]["data"]
    zz = table["z"] if "z" in table else np.zeros_like(table["y"])
    xyz = np.stack([table["x"], table["y"], zz], axis=1)
    # dump data and convert
    np.savetxt(".tmp.txt", xyz)
    BIN = os.path.dirname(pypotree.__file__) + "/bin"

    name = os.path.basename(file_path.replace(".smlm", ""))
    output_dir = os.path.join(os.path.dirname(file_path), "potree")
    try:
        print(
            "{BIN}/PotreeConverter .tmp.txt -f xyz -o {output_dir} -p {idd} --material ELEVATION --overwrite".format(
                BIN=BIN, output_dir=output_dir, idd=name
            )
        )
        os.system(
            '{BIN}/PotreeConverter .tmp.txt -f xyz -o "{output_dir}" -p "{idd}" --material ELEVATION --overwrite'.format(
                BIN=BIN, output_dir=output_dir, idd=name
            )
        )
        if zip:
            zip_name = file_path.replace(".smlm", ".potree")
            shutil.make_archive(
                zip_name, "zip", os.path.join(output_dir, "pointclouds", name)
            )
            shutil.rmtree(output_dir)
    except Exception:
        raise
    finally:
        os.remove(".tmp.txt")


def download(
    datasets,
    output_dir,
    file_patterns=["*.smlm"],
    include=["covers", "documentation", "files", "views"],
    conversion=False,
    sandbox=False,
    delimiter=",",
    extension=".csv",
):
    print(f"Files will be saved to: {output_dir}")
    for index, dataset_url in enumerate(datasets):
        if not dataset_url.startswith("http"):
            if sandbox:
                dataset_url = "https://sandbox.zenodo.org/record/" + dataset_url
            else:
                dataset_url = "https://zenodo.org/record/" + dataset_url
        print(f"======> Downloading dataset {index+1}/{len(datasets)}: {dataset_url}")
        rdf_url = dataset_url + "/files/rdf.yaml"
        data = urllib.request.urlopen(rdf_url)
        rdf = yaml.load(
            data.read()
            .decode("utf-8")
            .replace("!<tag:yaml.org,2002:js/undefined>", ""),
            Loader=yaml.FullLoader,
        )
        dataset_dir = os.path.join(output_dir, rdf["name"])
        os.makedirs(dataset_dir, exist_ok=True)
        download_url(
            resolve_url(rdf_url, "rdf.yaml"), os.path.join(dataset_dir, "rdf.yaml")
        )
        if "covers" in include and "covers" in rdf:
            for cover in rdf["covers"]:
                cover_file = os.path.join(
                    dataset_dir, "_covers", os.path.basename(cover)
                )
                os.makedirs(os.path.dirname(cover_file), exist_ok=True)
                download_url(resolve_url(rdf_url, cover), cover_file)
        if "documentation" in include and "documentation" in rdf:
            download_url(
                resolve_url(rdf_url, rdf["documentation"]),
                os.path.join(dataset_dir, os.path.basename(rdf["documentation"])),
            )
        if (
            "files" in include
            or "views" in include
            and rdf.get("attachments")
            and rdf["attachments"].get("samples")
        ):
            attachments = rdf["attachments"]
            for sample in attachments["samples"]:
                os.makedirs(os.path.join(dataset_dir, sample["name"]), exist_ok=True)
                if "views" in include:
                    for view in sample.get("views", []):
                        name = view.get("image_name")
                        file_path = os.path.join(dataset_dir, sample["name"], name)
                        if name:
                            # download the file
                            download_url(
                                resolve_url(rdf_url, sample["name"] + "/" + name),
                                file_path,
                            )

                if "files" not in include:
                    continue
                for file in sample.get("files", []):
                    file_path = os.path.join(dataset_dir, sample["name"], file["name"])
                    if any(
                        map(
                            lambda x: fnmatch.fnmatch(file["name"].lower(), x),
                            file_patterns,
                        )
                    ):
                        # download the file
                        download_url(
                            resolve_url(rdf_url, sample["name"] + "/" + file["name"]),
                            file_path,
                        )
                        # optionally, convert .smlm file to text file
                        if file_path.endswith(".smlm") and conversion:
                            print("Converting " + file_path + "...")
                            if extension == ".potree.zip":
                                convert_potree(file_path, True)
                            elif extension == ".potree":
                                convert_potree(file_path, False)
                            else:
                                convert_smlm(file_path, delimiter, extension)

        print("Done ")


def main():
    """
    Usage:
    ```
    python -m shareloc_utils.batch_download --datasets=https://sandbox.zenodo.org/record/891810 --output_dir=./output --conversion
    ```
    """
    import argparse

    parser = argparse.ArgumentParser(description="Batch downloading for ShareLoc.XYZ")
    parser.add_argument(
        "--datasets",
        default=[],
        help="A list of dataset URL or Zenodo ID, separated by comma",
    )
    parser.add_argument("--output_dir", default=None, help="output directory path")
    parser.add_argument(
        "--include",
        default="covers,documentation,files,views",
        help="The type of files to be downloaded, separated by comma. The default value is: covers,documentation,files,views",
    )
    parser.add_argument("--file_patterns", default="*.smlm,*.csv", help="file pattern")
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Use the sandbox site, used only when Zenodo IDs are provided for the datasets",
    )
    parser.add_argument(
        "--conversion",
        action="store_true",
        help="enable conversion to text file (e.g. csv)",
    )
    parser.add_argument(
        "--delimiter", default=",", help="the delimiter for text file conversion"
    )
    parser.add_argument(
        "--extension", default=".csv", help="file extension for text file conversion"
    )

    args = parser.parse_args()

    download(
        list(map(str.strip, args.datasets.split(","))),
        args.output_dir or tempfile.mkdtemp(),
        file_patterns=list(map(str.strip, args.file_patterns.split(","))),
        include=list(map(str.strip, args.include.split(","))),
        sandbox=args.sandbox,
        conversion=args.conversion,
        delimiter=args.delimiter,
        extension=args.extension,
    )


if __name__ == "__main__":
    main()
