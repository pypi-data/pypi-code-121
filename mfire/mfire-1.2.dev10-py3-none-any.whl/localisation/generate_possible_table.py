"""
Module permettant de generer le fichier excel fournit aux prévisionnistes.
Ce fichier excel contient tous les tableaux possibles
(selon les règles de SummarizedTable)
"""
import pandas as pd
import baseconvert
import xarray as xr
from mfire.localisation.table import SummarizedTable
from mfire.utils.date import Period


def export_df_as_excel(
    df_new, writer, sheet_name="Sheet1", global_text="Trimester value", **kwargs
):
    """
    Permet d'écrire le tableau sous excel.
    """
    workbook = writer.book

    sh = df_new.shape
    if global_text == "":
        srow = 1
    else:
        srow = 2
    if kwargs.get("index", True):
        scol = 1
    else:
        scol = 0
    if "add_col" in kwargs:
        # Permet de décaler l'écriture
        scol = scol + kwargs["add_col"]
    length = len(df_new.columns)
    if length <= 5:
        largeur = 25
    else:
        largeur = 15
    largeur = kwargs.get("largeur", largeur)

    df_new.to_excel(
        writer,
        sheet_name=sheet_name,
        startrow=srow,
        startcol=scol,
        header=False,
        index=False,
    )
    worksheet = writer.sheets[sheet_name]

    merge_format = workbook.add_format(
        {
            "text_wrap": True,
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "#668cff",
        }
    )

    header_format = workbook.add_format(
        {
            "text_wrap": True,
            "bold": True,
            "border": 1,
            "valign": "vcenter",
            "fg_color": "#b3c6ff",
        }
    )

    abc = workbook.add_format({"bg_color": "#b3c6ff"})

    red_format = workbook.add_format(
        {"bg_color": "#FFC7CE", "font_color": "#9C0006", "fg_color": "#b3c6ff"}
    )

    # Add a format. Green fill with dark green text.
    green_format = workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})

    if "risk" in kwargs:
        worksheet.conditional_format(
            0,
            scol,
            sh[0] + srow - 1,
            scol + sh[1] - 1,
            {"type": "blanks", "format": abc},
        )
        worksheet.conditional_format(
            0,
            scol,
            sh[0] + srow - 1,
            scol + sh[1] - 1,
            {
                "type": "cell",
                "criteria": ">=",
                "value": kwargs["risk"],
                "format": red_format,
            },
        )
        worksheet.conditional_format(
            0,
            scol,
            sh[0] + srow - 1,
            scol + sh[1] - 1,
            {
                "type": "cell",
                "criteria": "<",
                "value": kwargs["risk"],
                "format": green_format,
            },
        )
    for col_num, value in enumerate(df_new.columns.values):
        worksheet.write(srow - 1, col_num + scol, value)

    worksheet.write(srow - 1, 0, df_new.index.names[0])

    if kwargs.get("index", True):
        for row_num, value in enumerate(df_new.index.values):
            worksheet.write(row_num + srow, 0, value)
    if global_text != "":
        if length > 1:
            worksheet.merge_range(
                0, scol, 0, length - 1 + scol, global_text, merge_format
            )
        else:
            worksheet.write(0, scol, global_text, merge_format)
    #        worksheet.set_row(0, 55, merge_format)
    worksheet.set_row(srow - 1, 50, header_format)
    worksheet.set_column(0, 0, 20)
    worksheet.set_column(scol, col_num + scol, largeur)
    return writer


def visualize_as_table(set_list, fname="Table_sort.xls"):
    """
    Fonction qui va générer le fichier excel à partir du set de tableau.
    On sauve un à un les tableaux

    Args:
        set_list ([type]): [description]
        fname (str, optional): [description]. Defaults to "Table_sort.xls".
    """
    excel_file = fname
    writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")

    for elt in set_list:
        da = decode_table(elt)
        df = da.to_dataframe().reset_index()
        dfp = df.pivot(index="id", columns="period", values="elt")  # .transpose()
        dfp.reset_index(inplace=True)
        dfp = dfp.set_index("id")
        sheet_name = get_name_from_elt(elt)
        export_df_as_excel(
            dfp,
            writer=writer,
            sheet_name=sheet_name,
            global_text="Tableau",
            risk=1,
            index=True,
        )
    writer.save()


def get_name_from_elt(elt):
    """
    Retourne le nom correspondant à partir d'une liste/tuple
    en base 10 (incluant un string pour la période)
    Le nom est générique. Ainsi les lignes sont triées de la
    plus petite à la plus grande dans la fonction.

    Args:
        elt (tuple/list/frozenset): Le tableau à résumé. Par exemple ["3",7,2,0]

    Returns:
        str: Le  nom du talbeau
    """
    base = [k for k in elt if isinstance(k, str)][0]
    number = sorted([k for k in elt if not isinstance(k, str)])
    res = "P" + base
    for n in number:
        res += "_" + str(n)
    return res


def decode_table(table):
    """
    Ici on prend un tableau brut en entrée  et on fournit un dataArray en sortie.
    Les lignes sont "triées" dans la fonction (afin d'être de la plus petite
    à la plus grande).

    Args:
        tab (set/list/frozenset): Le nombre de période fait partie de
            la liste/tuple/set/frozenset en entrée ["nbPeriod",row1,row2,row3,row...]

    Returns:
        dataset : Le dataset correspondant au tableau.
    """
    l_out = list()
    nb_area = 0
    # On recupere le nombre de periode

    period_number = [int(elt) for elt in table if isinstance(elt, str)][0]
    row_number = sorted(
        [int(elt) for elt in table if not isinstance(elt, str)]
    )  # On peut avoir des numpy.int en plus des int.
    for elt in row_number:
        base_2 = baseconvert.base(int(elt), 10, 2)
        if isinstance(base_2, tuple):
            base_2 = list(base_2)
        else:
            base_2 = [
                base_2,
            ]

        while len(base_2) < period_number:
            base_2.insert(0, 0)
        l_out.append(base_2)
        nb_area += 1
    dout = xr.Dataset()
    dout["elt"] = (("id", "period"), l_out)
    dout.coords["id"] = [f"zone{k+1}" for k in range(nb_area)]
    dout.coords["period"] = [f"Period{k+1}" for k in range(period_number)]
    return dout


def generate_full_set(period_number=3):
    """
    On va essayer de boucler sur l'ensemble des sets
    On va :
       - Rendre les tableaux insensibles aux permutations de lignes
       - Supprimer les colonnes qui sont en double successivement
         (Period1 = Period2). Ces colonnes devront être regroupées.
       - Supprimer les colonnes où il n'y a que des 0

     Un set va être composée :
       - d'un string (décrivant le nombre de périodes présentes)
       - de plusieurs entier. Un entier par zone. Chaque entier sera converti
         en base 2 et permettra d'avoir l'info sur l'ensemble des périodes.

    Returns :
       Le set entier.
    """
    size = 2 ** period_number
    full_set = set()
    for i in range(size):
        for j in range(size):
            for k in range(size):
                small = frozenset({i, j, k})
                tmp = frozenset({str(period_number), i, j, k})
                # On va decoder chaque ligne
                if len(small) > 1:
                    tmp_bis = tmp
                    l1 = decode_table(tmp)
                    table_handler = SummarizedTable(
                        l1["elt"],
                        request_time="20200212T06",
                        full_period=Period("20200212T00", "20200212T20"),
                    )
                    tmp_bis = frozenset(table_handler.get_raw_table())
                    full_set.add(tmp_bis)
                else:
                    print("Skipping this %s" % small)
    return full_set


if __name__ == "__main__":
    full_data_set = generate_full_set(period_number=2)
    visualize_as_table(full_data_set)
