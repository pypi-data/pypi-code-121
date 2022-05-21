class Document:
    """Document object with directory and contents attributes."""
    def __init__(self, directory: str):
        self.directory = directory
        
        ## Checks
        if ".txt" not in self.directory:
            raise Exception("You must compare two text files.")

        ## Contents
        with open(self.directory, 'r') as f:
            self.contents = f.read()

def are_docs_same(original_dir: str, new_dir: str):
    """Checks if the contents of two files are exactly identical. Returns boolean."""
    # Get contents
    Original = Document(directory = original_dir)
    New = Document(directory = new_dir)

    # Check contents
    if Original.contents == New.contents:
        print("Contents match.")
        return True
    else:
        print("Contents do not match.")
        return False

def append_by_query(query: str, content: str, file_path: str, insert_above: bool = False):
    """
    Required args: query, content, and file path. 
    Optional args: insert_above

    Searches through the contents of the target file and inserts content a line below \
        the first occurence. 
    """
    
    # Open the file and get the lines
    with open(file_path, 'r') as f:
        data = f.readlines()

    # Check for the <title>
    found_the_line = False # exception handling
    for pos, line in enumerate(data):
        if query in line:
            found_the_line = True
            break
    
    # Quit the program if <title> wasn't found
    if not found_the_line:
        raise Exception(f"{query} not found in any lines of {file_path}.") 

    # Insert after? Increase line number by 1.
    if not insert_above:
        pos += 1

    # Append the string
    data.insert(pos, (content + '\n'))
    with open(file_path, 'w') as f:
        f.writelines(data)