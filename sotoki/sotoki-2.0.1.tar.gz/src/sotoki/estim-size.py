def utf8len(s):
    return len(s.encode("utf-8"))


# Nb FRONT Items:
#     21286479    # questions with answers and comments
#     5350000     # users (we don't store those without interactions)

#     T: 26,636,479
#     > @272b = 7,245,122,288b  # 6.75 GiB

# nb NO-FRONT Items:
#     100         # questions listing pages
#     100         # users listing pages
#     100         # assets (approx.)
#     90000       # Tags questions listing (approx. 61K tags, up to 133pg/tag)
#     1697        # tags listing pages (61059/36)
#     2184316     # Users images
#     17153       # questions images (extrapolated)

#     T: 2,293,466
#     > @ 264b = 605,475,024b  # 577.43 MiB

# Nb Redirect Item
#     31692495    # answers
#     10          # pagination

#     T: 31,692,495
#     > @264b = 8,366,818,680b  # 7.79 GiB

"""
# compute user paths & title len

import json
from slugify import slugify
from sotoki.utils.shared import Global


def utf8len(s):
    return len(s.encode("utf-8"))


total = 0
all_users_ids_fpath = Global.conf.build_dir / "all_users_ids.json"
with open(all_users_ids_fpath, "r") as fh:
    all_users_ids = set(json.load(fh))
for user_id in all_users_ids:
    print(user_id)
    user = Global.database.get_user_full(user_id)
    if user is None:
        name = str(user_id)
    else:
        name = user.get("name", str(user_id))
    del user
    slug = slugify(name)
    path = f"users/{user_id}/{slug}"
    title = f"User {name}"
    total += utf8len(path) + utf8len(title)
print(f"{total=}")
"""

# compute user paths & title len

import json
from slugify import slugify
from sotoki.utils.html import get_slug_for
from sotoki.utils.shared import Global

total = 0
it = 0
cursor = None
while cursor != 0:
    cursor, keys = Global.database.conn.scan(cursor or 0, match="Q:*", count=1000)
    for key in keys:
        it += 1
        print(it)
        qid = int(key.split(b":", 1)[-1])
        title = Global.database.get_question_title_desc(qid)["title"]
        slug = get_slug_for(title)
        path = f"questions/{qid}/{slug}"
        total += utf8len(path) + utf8len(title)
print(f"{total=}")


import humanfriendly


def utf8len(s):
    return len(s.encode("utf-8"))


def fmt(s):
    return humanfriendly.format_size(s, binary=True)


entry_size1 = 264
entry_size2 = 143
front = 8
img_path_len = utf8len("images/1234567899.webp")  # 22
ans_redir_len = utf8len("a/99000000")
support_path_title_len = 120

nb_questions = 21286479
nb_users = 5310770
nb_users_imgs = 2184316
nb_quest_imgs = 17153
nb_answers = 31692495
nb_support_pages = 90000

# computed
users_path_title_len = 203547070
questions_path_title_len = 2646318685

for entry_size in (entry_size1, entry_size2):
    grand_total = 0
    print(f"With {entry_size=}")
    # s_questions =
    s_users_profiles = nb_users * (entry_size + front) + users_path_title_len
    print(f"{s_users_profiles=}", fmt(s_users_profiles))
    grand_total += s_users_profiles

    s_questions_pages = nb_questions * (entry_size + front) + questions_path_title_len
    print(f"{s_questions_pages=}", fmt(s_questions_pages))
    grand_total += s_questions_pages

    s_users_imgs = nb_users_imgs * (entry_size + img_path_len)
    print(f"{s_users_imgs=}", fmt(s_users_imgs))
    grand_total += s_users_imgs

    s_quest_imgs = nb_quest_imgs * (entry_size + img_path_len)
    print(f"{s_quest_imgs=}", fmt(s_quest_imgs))
    grand_total += s_quest_imgs

    s_answ_redir = nb_answers * (entry_size + ans_redir_len)
    print(f"{s_answ_redir=}", fmt(s_answ_redir))
    grand_total += s_answ_redir

    s_support = nb_support_pages * (entry_size + support_path_title_len)
    print(f"{s_support=}", fmt(s_support))
    grand_total += s_support

    print(f"{grand_total=}", fmt(grand_total))
    print("-----")
