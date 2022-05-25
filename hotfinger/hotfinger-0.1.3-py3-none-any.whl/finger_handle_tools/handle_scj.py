import json

from cp_common.log import logger

hotfinger = []


hotfinger_set = set()
scj_set = set()

with open("../data/hotfinger_v1.json", "r") as f:
    hotfinger = json.load(f)
    for item in hotfinger:
        hotfinger_set.add(item["name"].lower())


def remove_null(data):
    new_data = []
    for item in data:
        new_item = {}
        for k, v in item.items():
            if v != "":
                new_item[k] = v
        new_data.append(new_item)
        scj_set.add(item["name"].lower())
    return new_data


def diff_add(data):
    s = scj_set.difference(hotfinger_set)
    logger.info(s)
    logger.info(len(s))
    new_data = []
    for item in data:
        if item["name"].lower() in s:
            new_data.append(item)
    return new_data


def no_regex(data):
    new_data = []
    for item in data:
        new_item = {}
        title_content = None
        header_content = None
        html_content = None

        if "regex" not in item:
            content = ""
            if "title" in item:
                title_content = 'title="' + item["title"].strip() + '"'
                content = title_content
            if "headers" in item:
                if len(content) > 0:
                    content = content + " || "
                header_content = 'header="' + item["headers"].strip() + '"'
                content = content + header_content

            if "html" in item:
                if len(content) > 0:
                    content = content + " || "
                html_content = 'body="' + item["html"].strip() + '"'
                content = content + html_content

            new_item = {
                "_id": {"$oid": item["id"]},
                "name": item["name"],
                "content": {"/": content},
                "tags": ["scj"],
            }
            new_data.append(new_item)
        else:
            # TODO: 进一步处理正则
            new_item = {
                "_id": {"$oid": item["id"]},
                "name": item["name"],
                "content": {"/": "body=" + item["regex"].strip() + '"'},
                "tags": ["scj"],
            }
            new_data.append(new_item)
    return new_data


def yes_regex(data):
    pass


def main():
    with open("scj.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)
        # logger.info(data["data"])
        data = remove_null(data["data"])

    with open("scj_v2.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    data = diff_add(data)

    with open("scj_v3.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    data = no_regex(data)
    logger.info(len(data))
    with open("scj_v4.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
