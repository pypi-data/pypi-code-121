import sys
import os
import re
from pathlib import Path

import questionary
from questionary import print as qprint

import p1
from p1.colors import *
from p1.utils import cprint
from p1.utils import _assert
from p1.utils import data2json
from p1.jsonfile import JsonFile
from p1 import P1STYLE

BASEDIR = Path(os.environ.get("P1_DIR") or p1.get_config().get("basedir", "~/p1")).expanduser()

# resquício dos comandos do tst
site = p1.get_site("prog1")

def validate_use(args):
    option_args = [o for o in args if o.startswith("--")]
    try:
        assert all(o in {"--overwrite", "--dir", "-o", "-d"} for o in option_args)
    except AssertionError as e:
        return False

    return True


def unidade(u):
    try:
        numero = re.search("\d+|$", u).group()
        if numero.isdigit():
            return f"u{numero}"

    except TypeError as e:
        # unit é None
        pass

    return "ex"


def main():
    # separa argumentos
    args = sys.argv[2:]
    _assert(validate_use(args), syntax_help())

    # determina especificação da atividade a buscar
    spec = next((a for a in args if not a.startswith("--")), "@")

    # opção --overwrite?
    overwrite = any(a == "--overwrite" for a in args)

    if os.path.isdir(spec):
        # "p1 checkout <DIR>": atualização do checkout em <DIR>
        p1_filename = f"{args[0]}/.p1/assignment.json"
        _assert(os.path.exists(p1_filename), f"Diretório {args[0]} não contém atividade de p1")
        p1file = JsonFile(p1_filename)
        activity_dir = args[0]
        email, key = p1file["user"], p1file["iid"]

    else:
        # ou é <pattern>[@<email>]
        # ou é um IID
        # ou foi invocação sem argumentos (nesse caso spec será '@')
        pattern, email = spec.split("@") if "@" in spec else (spec, "")
        questionary.print("Identificando atividades no servidor", "bold green")
        response = site.get(f"/available?email={email}")
        if response.status_code != 200:
            data = response.json()
            print(data["messages"][0])
            sys.exit(1)

        available = response.json()["available"]
        filtered = [act for act in available if pattern.lower() in act["label"].lower()]
        if not filtered and pattern.isdigit():
            activity_iid = int(pattern)
            filtered = [act for act in available if act['iid'] == activity_iid]
        _assert(filtered, f"nenhuma atividade encontrada: {pattern}")

        opcoes = []
        for (i,a) in enumerate(filtered):
           opcoes.append(questionary.Choice(f'{a["dirname"]}: {a["label"]}', value=i))

        idx_opcao = questionary.select(
            "Atividades disponíveis: ",
            opcoes,
            style=P1STYLE,
            instruction="(use as setas para escolher)",
            use_jk_keys=True,
        ).ask()
        iid = str(filtered[idx_opcao]["iid"])
        activity_dir = str(BASEDIR / filtered[idx_opcao]["dirname"])

    assignments = Path('~/p1').expanduser().rglob('.p1/assignment.json')
    assignments = [p for p in assignments]
    iguais = [p for p in assignments if str(JsonFile(p)['iid']) == iid]
    if len(iguais) > 1:
        qprint('Erro. Há vários diretórios com a mesma atividade:', style="bold red")
        for a in iguais:
            directory = str(a.parent.parent).replace(str(Path.home()), "~")
            qprint(directory, style="#bbbbbb")
        qprint("Apague os diretórios desnecessários antes de prosseguir.", style="bold #ff9d00")
        qprint("Checkout abortado.", style="bold #ff9d00")
        sys.exit(1)
        
    if len(iguais) == 1 and iguais[0].parent.parent != activity_dir:
        iguais[0].parent.parent.rename(activity_dir)

    checkout(iid, activity_dir, overwrite)


def syntax_help():
    return ("Usage: p1 checkout <key>[@<site>] [<directory>]\n"
           "       p1 checkout <url> [<directory>]\n\n"
           "   or: p1 checkout\n"
           "       (inside a p1 directory)")


def save_file(filename, content, mode):
    def octal_mode(mode):
        return {
            (False , False): 0o444,
            (False ,  True): 0o555,
            (True  , False): 0o644,
            (True  ,  True): 0o755
        }["w" in mode, "x" in mode]

    subdirs = os.path.dirname(filename)
    if not os.path.isdir(subdirs):
        os.makedirs(subdirs)

    with open(filename, encoding="utf-8", mode="w") as f:
        f.write(content)

    os.chmod(filename, octal_mode(mode))


def save_selected_files(savetable):
    for i in range(len(savetable)):
        line = savetable[i]
        if line[2] == 'unchanged':
            savetable[i][3] = 'skipped'
            continue

        try:
            filename = line[1]
            if os.path.exists(filename):
                os.chmod(filename, 0o644)

            mode = line[0].get('mode', '644')
            save_file(filename, line[0]['content'], mode)
            savetable[i][3] = 'saved'

        except (IOError, OSError) as e:
            savetable[i][3] = 'failed'
            assert False, f"CRITICAL ERROR: failed saving file '{line[1]}'"


def get_save_table(files, basedir):
    """
    Return a table that helps saving files to FS.
    Each line of the table has 4 columns:
    - the file itself
    - the filename to be saved to
    - the situation wrt to current FS: notfound, unchanged, changed
    - an empty cell to write the final status after saving
    """
    savetable = []
    for f in files:
        save_name = "%s/%s" % (basedir, f['name'])
        if not os.path.exists(save_name):
            savetable.append([f, save_name, 'notfound', None])
        else:
            # a version of the file already exists
            old_contents = open(save_name, encoding='utf-8').read()
            new_contents = f['content']
            if old_contents == new_contents:
                savetable.append([f, save_name, 'unchanged', None])
            else:
                savetable.append([f, save_name, 'changed', None])

    return savetable


def checkout(iid, destdir, overwrite_allowed):
    """checkout activity/assignment from site/collection"""

    # fetch activity
    cprint(LGREEN, "Buscando atividade no servidor (%s)" % iid)
    activity, response = site.get_activity(iid)
    if response.status_code == 404:
        activity, response = site.get_directory(iid)

    if response.status_code == 401:
        cprint(LRED, 'Checkout não autorizado (%s)' % site.last_response.status_code)
        cprint(WHITE, 'Execute: p1 login')
        return

    elif response.status_code == 404:
        cprint(LRED, 'Atividade não encontrada (%s)' % site.last_response.status_code)
        return

    elif response.status_code in [400, 412]:
        cprint(LRED, 'Checkout não permitido (%s)' % site.last_response.status_code)
        cprint(LRED, 'Problema: %s' % site.last_response.json()['messages'][0])
        return

    _assert(activity, "Não foi possível fazer o checkout (%s)" % response.status_code)

    # analyze what must be saved to FS
    savetable = get_save_table(activity['files'], destdir)
    num_to_overwrite = 0
    for line in savetable:
        if line[2] == 'changed':
            num_to_overwrite += 1
            if not overwrite_allowed: cprint(LRED, f"{line[1]}")

    if num_to_overwrite and not overwrite_allowed:
        cprint(YELLOW, "Estes arquivos serão alterados! Confirma? (s/N)? ", end="")
        if input() != "s":
            cprint(YELLOW, 'Checkout cancelado pelo usuário')
            sys.exit(1)

    # save 'notfound' and 'changed' files
    save_selected_files(savetable)
    num_saved = 0
    for line in savetable:
        filename = line[1].replace(str(Path.home()), "~")
        if line[3] == 'skipped':
            cprint(RESET, f"ignorando: {filename}")
        elif line[3] == 'saved':
            cprint(LCYAN, f" salvando: {filename}")
            num_saved += 1

    cprint(LGREEN, f"{num_saved} arquivo(s) gravados")

    content = data2json({
            "site": site.name,
            "key": iid,
            "iid": activity.get('iid'),
            "user": activity.get('user'),
            "dirname": activity.get('dirname'),
            "full_resource": activity['_response'].json() if '_response' in activity else None
        })
    save_file(f'{destdir}/.p1/assignment.json', content, "rw")
