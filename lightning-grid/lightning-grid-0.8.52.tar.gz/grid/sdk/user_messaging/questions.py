from typing import List


def datastore_ask_if_should_resume_upload(source: str) -> str:
    return (
        f"Your previous upload of {source} did not complete. Would you like to complete it? \n"
        f"[y] yes (progress will resume where you left off)\n"
        f"[n] no (progress will be deleted)\n"
    )


def datastore_ask_if_should_resume_after_files_modified(file_list: List[str]) -> str:
    start_text = "The following files have been modified since uploading began: \n"

    file_list_string = ""
    for file in file_list:
        file_list_string += f"- {file}\n"

    end_text = (
        "Would you like to continue uploading the remaining files? Files already "
        "uploaded will not reflect these changes. \n"
        "[y] continue \n"
        "[n] restart (current upload progress will be lost)\n"
    )

    return f"{start_text}{file_list_string}{end_text}"
