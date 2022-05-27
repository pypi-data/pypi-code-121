from robertcommonbasic.basic.os.file import scan_files


def test_scan_files():
    files = scan_files(f"E:/Beop/Code/Git/datapushserver/file/real/*/20220323/**", False)
    print(files)

test_scan_files()