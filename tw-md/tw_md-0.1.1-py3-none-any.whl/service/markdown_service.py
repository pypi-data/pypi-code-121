import codecs
from ..domain.repository import Repository


class MarkdownService:
    def __init__(self) -> None:
        self.__table_header = (
            "Aula | Video | Commit | Link\n------ | ------ | ------ | ------\n"
        )

    def create_repository_commmits_table(
        self, repository: Repository, filename: str
    ) -> None:
        with open(filename, "w", encoding="UTF-8") as file:
            file.write(self.__table_header)
            for commit in repository.commits[::-1]:
                table_row = self.__get_table_row(
                    repository.owner, repository.name, commit.sha, commit.message
                )
                file.write(table_row)

    def __get_table_row(
        self, owner: str, repository: str, sha: str, message: str
    ) -> str:
        link = (
            f"[Download](https://github.com/{owner}/{repository}/archive/{sha}.zip)\n"
        )
        return f"Aula <numero_da_aula> | <numero_do_vídeo> | {message} | {link}"
