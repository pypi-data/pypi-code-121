import pandas as pd

# put all changed lines in a file into one string
def squash_changes(change):
    changes = []
    for line in change:
        changes.append(line[1])
    change = '\n'.join(changes)
    return change

# takes list of parsed_diffs and spits out the squashed diffs
def iterate_over_diffs(parsed_diff):
    
    files = []
    for file in parsed_diff:
        file['deleted'] = squash_changes(file['deleted'])
        file['added'] = squash_changes(file['added'])
        files.append(file)
    return files


# takes parsed_diffs list, and puts each element into df row with "added" and "deleted" rows
def put_into_df(parsed_diffs):
    
    # create added, deleted list
    added = []
    deleted = []
    for parsed_diff in parsed_diffs:
        added.append(parsed_diff['added'])
        deleted.append(parsed_diff['deleted'])
        
    # create df
    data = {'added': added, 'deleted': deleted}
    df = pd.DataFrame(data=data)
    
    return df

# takes df of added and deleted fields. Rows are each file changed.
# prompt is a list of dicts. Dicts contain added and deleted fields
def create_prompt(df):
    prompt = []
    for index, row in df.iterrows():
#         add = '\n'.join(row.added)
#         delete = '\n'.join(row.deleted)
        prompt.append({'added: ' + row.added +  '\n\n' + 'deleted: ' + row.deleted})
    return prompt

