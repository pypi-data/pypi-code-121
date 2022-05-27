import os
import re
import wikipedia
import requests
import json
from pathlib import Path
import time
from Levenshtein import distance as levenshtein_distance
from functools import lru_cache


def match(dbs, tree, db_separator="_", levenshtein_num=4):

    output = []
    difference_threshold = int(levenshtein_num)
    for db in dbs:
        for db_name in db:
            suggestions = []
            genus_match = []
            species_match = []
            try:
                genus_name = db_name.split(db_separator, 1)[0]
                species_name = db_name.split(db_separator, 1)[1]
            except:
                break

            found_match = False
            for tree_name in tree:
                if db_name == tree_name:
                    found_match = True
                    break
                elif levenshtein_distance(db_name, tree_name) < difference_threshold:
                    suggestions.append(tree_name)
                elif re.match(rf".*{species_name}", tree_name):
                    species_match.append(tree_name)
                elif re.match(rf"{genus_name}*", tree_name):
                    genus_match.append(tree_name)

            if found_match:
                output.append(db_name)
            else:
                output.append([db_name, suggestions, species_match, genus_match])

    return output


def read_files(db_path, tree_path):
    dbs = []
    trees = []
    filenames = []
    if os.path.isdir(db_path):
        filenames = os.listdir(db_path)
    else:
        filenames.append(os.path.basename(db_path))
        db_path = os.path.dirname(db_path)

    for filename in filenames:
        if not filename.startswith('.'):
            with open(os.path.join(db_path, filename), 'r', encoding="utf-8") as f:  # open in readonly mode
                db = []
                for line in f:
                    # Get name for every line
                    name = line.split(",", 1)[0]
                    db.append(name)

                # Remove first line of db (info line)
                db.pop(0)
                dbs.append(db)

    filenames = []
    if os.path.isdir(tree_path):
        filenames = os.listdir(tree_path)
    else:
        filenames.append(os.path.basename(tree_path))
        tree_path = os.path.dirname(tree_path)

    for filename in filenames:
        if not filename.startswith('.'):
            with open(os.path.join(tree_path, filename), 'r', encoding="utf-8") as f:  # open in readonly mode
                fname = os.path.basename(f.name)
                tree = []
                copy = False
                # .nex file read
                if fname.endswith('.nex'):
                    for line in f:
                        if line.strip() == "TAXLABELS":
                            copy = True
                            continue
                        elif line.strip() == ";":
                            break
                        elif copy:
                            tree.append(line.strip())
                # .csv (truth db) file read
                elif fname.endswith('.csv'):
                    for line in f:
                        # Get name for every line
                        name = line.split(",", 1)[0]
                        tree.append(name)
                    # Remove first line of tree (info line)
                    tree.pop(0)
                trees.append(tree)

    return dbs, tree

def append_id(filename):
    p = Path(filename)
    return "{0}_{2}{1}".format(Path.joinpath(p.parent, p.stem), p.suffix, time.time())

# Takes the completed taxa_list and writes a new file that includes the new taxa names and the rest of the data from db_path
# TODO: handle multiple input dbs, perhaps with search
def write_file(taxa_list, db_path):

    outfile_path = append_id(db_path)

    with open(outfile_path, "w", encoding="utf-8") as outf:

        with open(db_path, 'r', encoding="utf-8") as f:  # open in readonly mode

            i = 0

            for line in f:

                if i == 0:
                    outf.write(line)
                    i += 1
                else:
                    csv_line = line.split(",")
                    # Replace first line with new name, only if not blank
                    if taxa_list[i - 1] != "":
                        csv_line[0] = taxa_list[i - 1]
                    outf.write(",".join(csv_line))
                    i += 1


def get_wiki_image(search_term):
    WIKI_REQUEST = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='
    try:
        result = wikipedia.search(search_term, results=1)
        wikipedia.set_lang('en')
        wikipage = wikipedia.WikipediaPage(title=result[0])
        title = wikipage.title
        response = requests.get(WIKI_REQUEST + title)
        json_data = json.loads(response.text)
        img_link = list(json_data['query']['pages'].values())[0]['original']['source']
        return img_link
    except:
        return 0


@lru_cache(maxsize=None)
def get_wiki_section(topic, n=10):
    return wikipedia.summary(topic, sentences=n)


# Takes list and returns wiki first paragraph for each entry
def get_wiki_info(list):
    wiki_entries = {}
    for species in list:
        try:
            wiki_entries[species] = get_wiki_section(species)
        except:
            wiki_entries[species] = "No info"
    return wiki_entries


def write_wiki_file(new_data, path, fname):
    try:
        with open(f"{path}/{fname}", "r") as f:
            current_data = json.load(f)
            full_data = current_data | new_data
        with open(f"{path}/{fname}", "w") as f:
            json.dump(full_data, f, indent=6, sort_keys=True)
    except:
        with open(f"{path}/{fname}", "w") as f:
            json.dump(new_data, f, indent=6, sort_keys=True)


def read_wiki_file(path, fname):
    try:
        with open(f"{path}/{fname}", 'r') as f:
            dict = json.load(f)
        return dict
    except:
        return {}


# checks information in info and ensures it has entries for every possible match
# returns list of all missing species. Empty list is fully complete.
def validate_info(info, suggestions):
    missing_info = []
    for suggestion in suggestions:
        # match found
        if type(suggestion) is str:
            continue
        for sub_suggestion in suggestion:
            # list of suggestions
            if type(sub_suggestion) is list:
                for sub_sub_suggestion in sub_suggestion:
                    if sub_sub_suggestion not in info:
                        missing_info.append(sub_sub_suggestion)
            elif sub_suggestion not in info:
                missing_info.append(sub_suggestion)
    # return set to weed out duplicates
    return set(missing_info)


if __name__ == '__main__':
    info = read_wiki_file("dat/info", "info.json")
    suggestions = match("dat/db", "dat/tree")
    missing_info = validate_info(info, suggestions)
    wiki_info = get_wiki_info(missing_info)
    write_wiki_file(wiki_info, "dat/info", "info.json")
