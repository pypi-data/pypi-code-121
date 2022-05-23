from io import BytesIO
import oead

from bcml.mergers.rstable import (
    calculate_size,
    _get_sizes_in_sarc,
    get_stock_rstb,
    EXCLUDE_EXTS,
    EXCLUDE_NAMES,
)
from bcml.util import (
    SARC_EXTS,
    BYML_EXTS,
    AAMP_EXTS,
    get_canon_name,
    unyaz_if_needed,
    get_settings,
)
from hyrule_builder.unbuilder import _unbuild_sarc
from pathlib import Path
from time import time
from typing import Union
from rstb import ResourceSizeTable
from shutil import rmtree


def unbuild_sarc(file: Union[Path, bytes]):

    # Locate and backup source file
    sarc_path = Path(file) if isinstance(file, str) else file
    out: str = sarc_path.absolute()
    sarc_path.rename(f"{sarc_path.stem}.tmp")

    # Read and unpack SARC
    sarc = oead.Sarc(unyaz_if_needed(sarc_path.read_bytes()))
    _unbuild_sarc(sarc, out, skip_texts=True)

    # Delete the original file
    sarc_path.unlink()


def to_sarc_key(src: Path, rel: Path, remove_suffix: bool = False) -> str:

    if remove_suffix:
        src = src.with_suffix("")

    return src.relative_to(rel).as_posix()


def build_yaml(file: Path) -> bytes:
    real_file = file.with_suffix("")
    data: bytes
    if real_file.suffix in BYML_EXTS:
        data = oead.byml.to_binary(oead.byml.from_text(file.read_text("utf-8")), True)
    elif real_file.suffix in AAMP_EXTS:
        data = oead.aamp.ParameterIO.from_text(file.read_text("utf-8")).to_binary()
    else:
        raise TypeError("Can only build AAMP or BYML files from YAML")
    if real_file.suffix.startswith(".s"):
        data = oead.yaz0.compress(data)

    return data


def build_sarc(folder: Union[Path, str]) -> Path:

    # Locate and backup source folder
    source = Path(folder) if isinstance(folder, str) else folder
    out: Path = Path(source.absolute())
    source = source.rename(f"{source}.tmp")

    # Build folder
    sarc = oead.SarcWriter(oead.Endianness.Big)

    for file in source.rglob("**/*"):

        if file.is_dir():
            if file.suffix in SARC_EXTS:
                sarc.files[to_sarc_key(file, source)] = build_sarc(file).read_bytes()
            continue

        if file.suffix == ".yml":
            sarc.files[to_sarc_key(file, source, True)] = build_yaml(file)

        else:
            sarc.files[to_sarc_key(file, source)] = file.read_bytes()

    if out.suffix.startswith(".s") and out.suffix != ".sarc":
        sarc_data = oead.yaz0.compress(sarc.write()[1])
    else:
        sarc_data = sarc.write()[1]

    out.write_bytes(sarc_data)

    # Delete the original folder
    rmtree(source)

    return out


def cout(value: str):
    print(value, end="\r")


def main():

    # Start tracking
    start = time()
    i: int = 0

    # Get/set meta data
    mod_dir = Path("D:\\Botw\\Cemu (Freecam)\\graphicPacks\\BreathOfTheWild_Randomizer")
    rstb: ResourceSizeTable = get_stock_rstb()

    for folder in mod_dir.glob("**/*"):

        if folder.is_dir() and (folder.name == "content" or folder.name == "aoc"):

            for file in folder.glob("**/*"):

                if file.is_dir():
                    if file.suffix in SARC_EXTS:
                        file = build_sarc(file)

                if file.is_file():
                    i += 1
                    if file.suffix in SARC_EXTS:
                        values: dict = _get_sizes_in_sarc(file, True)

                        for name, size in values.items():

                            if Path(name).suffix in EXCLUDE_EXTS:
                                continue

                            i += 1
                            cout(f"Added {i} values.")
                            rstb.set_size(name, size)

                    if file.suffix.replace(".s", ".") in EXCLUDE_EXTS:
                        continue
                    if file.name.replace(".s", ".") in EXCLUDE_NAMES:
                        continue

                    rstb.set_size(
                        get_canon_name(file.relative_to(mod_dir)), calculate_size(file)
                    )
                    cout(f"Added {i} values.")

    print("\nSerializing ResourceSizeTable...")

    rstb_path = Path(
        f"{mod_dir}\\content\\System\\Resource\\ResourceSizeTable.product.srsizetable"
    )

    buf = BytesIO()
    rstb.write(buf, be=get_settings("wiiu"))
    rstb_path.write_bytes(oead.yaz0.compress(buf.getvalue()))

    end = time()
    print(f"Operation completed in {end-start}.")


if __name__ == "__main__":
    main()
