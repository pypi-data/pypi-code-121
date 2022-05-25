from autoflake import fix_code
import black


def reformat_code_str(code_str: str) -> str:
    # Use autoflake to remove unused model imports instead of trying to crawl the entire manifest and figure
    # out which ones are being used.
    code_str = fix_code(code_str, remove_all_unused_imports=True)
    return black.format_str(code_str, mode=black.Mode(line_length=110))
