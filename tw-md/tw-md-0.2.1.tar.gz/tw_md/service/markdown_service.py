import codecs
import re

from tw_md.errors.github_errors import CommitMessageOutOfPatternException
from ..domain.repository import Repository


class MarkdownService:
    def __init__(self) -> None:
        self.__table_header = (
            "Aula | Video | Commit | Link\n------ | ------ | ------ | ------\n"
        )

    def create_repository_commmits_table(
        self, repository: Repository, filename: str, pattern: bool = False
    ) -> None:
        with open(filename, "w", encoding="UTF-8") as file:
            file.write(self.__table_header)
            for commit in repository.commits[::-1]:
                try:
                    if pattern:
                        table_row = self.__get_table_row_with_pattern(
                            repository.owner,
                            repository.name,
                            commit.sha,
                            commit.message,
                        )
                    else:
                        table_row = self.__get_table_row(
                            repository.owner,
                            repository.name,
                            commit.sha,
                            commit.message,
                        )
                    file.write(table_row)
                except:
                    continue

    def __get_table_row(
        self, owner: str, repository: str, sha: str, message: str
    ) -> str:
        link = (
            f"[Download](https://github.com/{owner}/{repository}/archive/{sha}.zip)\n"
        )
        return f"Aula <numero_da_aula> | <numero_do_vídeo> | {message} | {link}"

    def __get_table_row_with_pattern(
        self, owner: str, repository: str, sha: str, message: str
    ) -> str:
        if re.match("[0-9]{2}:[0-9]{2} - [a-z A-Z]+", message):
            lesson = message.split(":")[0]
            video = ":".join(message.split(":")[1:])
            link = f"[Download](https://github.com/{owner}/{repository}/archive/{sha}.zip)\n"
            return f"Aula {lesson} | Vídeo {video} | {message} | {link}"
        raise CommitMessageOutOfPatternException()
