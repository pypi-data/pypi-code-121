from datetime import datetime
import ftplib
import os


def _get_fftp_files(
    ftp: ftplib.FTP, path: str, files: list, dirs: list, file_dates: list
):

    lst: list = []

    year = datetime.now().strftime("%Y")

    ftp.dir(path, lst.append)
    for item in lst:
        parts = item.split(maxsplit=8)
        fullname = f"{path}/{parts[-1]}"
        if item.startswith("d"):
            dirs.append(fullname)
            _get_fftp_files(ftp, fullname, files, dirs, file_dates)
        else:
            if ":" in parts[7]:
                parts[7] = year
            date = datetime.strptime(f"{parts[5]} {parts[6]} {parts[7]}", "%b %d %Y")
            # datestr = date.strftime("%Y%m%d")
            files.append(fullname)
            file_dates.append(date)


def _makedirs(ftp: ftplib.FTP, path: str, remote_dirs: set):
    assert path.startswith("/")
    if path in remote_dirs:
        return

    dirs = path.split("/")[1:]

    ftp.cwd("/")
    for dir in dirs:
        try:
            ftp.cwd(dir)
            continue
        except:
            ftp.mkd(dir)
            ftp.cwd(dir)

    remote_dirs.add(path)


class FTP:
    def __init__(self, host: str, port: int, username: str, password: str):
        self._ftp = ftplib.FTP()
        self._ftp.connect(host, port)
        self._ftp.login(username, password)

    @property
    def ftp(self):
        return self._ftp

    def close(self):
        self._ftp.close()

    def list_all(self, path: str) -> tuple[list, list, list]:
        files: list = []
        dirs: list = []
        file_dates: list = []

        _get_fftp_files(self._ftp, path, files, dirs, file_dates)
        return files, dirs, file_dates

    def push_file(self, local_path: str, remote_path: str):
        dirname = os.path.dirname(remote_path)
        self.makedirs(dirname)
        self._ftp.cwd(dirname)
        with open(local_path, "rb") as f:
            self._ftp.storbinary(f"STOR {os.path.basename(remote_path)}", f)

    def try_push_dir(self, local_path: str, remote_path: str):
        """将本地目录推送到远程目录，如果远程文件存在，则忽略"""

        assert remote_path.startswith("/")

        remote_files, remote_dirs, _ = (set(x) for x in self.list_all(remote_path))

        _makedirs(self._ftp, remote_path, remote_dirs)
        self._ftp.cwd(remote_path)

        for root, dirs, files in os.walk(local_path):
            remote_dir = os.path.relpath(root, local_path)
            remote_dir = os.path.join(remote_path, remote_dir).replace("\\", "/")
            self._ftp.cwd(remote_dir)

            # 创建目录
            for dir in dirs:
                try:
                    self._ftp.mkd(dir)
                except:
                    pass

            # 推送文件
            for file in files:
                local_full_name = os.path.join(root, file)
                local_relpath = os.path.relpath(local_full_name, local_path)
                remote_file = os.path.join(remote_path, local_relpath).replace(
                    "\\", "/"
                )
                if remote_file in remote_files:
                    continue
                with open(local_full_name, "rb") as f:
                    self._ftp.storbinary(f"STOR {file}", f)
                    print(f"ftp push:{local_relpath} -> {remote_file}")

    def makedirs(self, path: str):
        assert path.startswith("/")
        dirs = path.split("/")[1:]
        self._ftp.cwd("/")
        for dir in dirs:
            try:
                self._ftp.cwd(dir)
                continue
            except:
                self._ftp.mkd(dir)
                self._ftp.cwd(dir)
