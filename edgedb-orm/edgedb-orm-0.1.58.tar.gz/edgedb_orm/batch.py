import typing as T
import re
import asyncio
from edgedb import AsyncIOClient
from pydantic import BaseModel
from .constants import ALIAS_PATTERN, random_str, chunk_list, flatten_list
from .execute import query as execute_query


class BatchException(Exception):
    pass


class Batch(BaseModel):
    client: AsyncIOClient
    print_status: bool = True
    debug: bool = False
    mutation_lines: T.List[str] = []
    query_variables: T.Dict[str, T.Any] = {}

    class Config:
        arbitrary_types_allowed = True

    def add(self, line: str, variables: T.Dict[str, T.Any] = None) -> None:
        """for add, update, delete"""
        aliases = re.findall(ALIAS_PATTERN, line)
        for alias in aliases:
            # find all instances of that alias, change the variable
            random_model_id = random_str(10)
            new_alias = f"{alias}{random_model_id}"
            if new_alias in self.query_variables:
                raise BatchException(f"Found a duplicate new alias {new_alias}")
            if alias in variables:
                variables[new_alias] = variables[alias]
                del variables[alias]
                pattern_to_sub = fr"(>\$)({alias})(\W*)"
                line = re.sub(pattern_to_sub, fr"\1{new_alias}\3", line)

        self.mutation_lines.append(line)
        self.query_variables.update(variables)

    async def commit_chunk(
        self, mutation_lines_chunk: T.List[str], chunk_id: int
    ) -> T.List[str]:
        lines_strs: T.List[str] = []
        model_name_strs: T.List[str] = []
        for i, line in enumerate(mutation_lines_chunk):
            model_name = f"model{i}"
            line_str = f"{model_name} := ({line})"
            model_name_strs.append(model_name)
            lines_strs.append(line_str)
        lines_strs.append(f'models := {{{", ".join(model_name_strs)}}}')
        s = f"WITH {','.join(lines_strs)} SELECT models {{ id }};"
        # now remove the non-used aliases from variables
        used_aliases = re.findall(ALIAS_PATTERN, str(lines_strs))
        valid_variables = {
            key: val for key, val in self.query_variables.items() if key in used_aliases
        }
        raw_d = await execute_query(
            client=self.client,
            query_str=s,
            variables=valid_variables,
            print_query=False,
        )
        ids = [d["id"] for d in raw_d]
        if self.print_status:
            print(f"executed {chunk_id=}, {ids=}")
            if self.debug:
                print(f"QUERY STRING: {s=}")
        return ids

    async def commit(self, chunk_size: int = None) -> T.List[str]:
        """returns a list of ids from the nodes touched.
        It is atomic so if you have a chunk size it will lose the atomic nature.
        But also it will fail if it has over ~20 objects"""
        if chunk_size:
            chunks = chunk_list(lst=self.mutation_lines, chunk_size=chunk_size)
        else:
            chunks = [self.mutation_lines]
        proms = [
            self.commit_chunk(mutation_lines_chunk=chunk, chunk_id=i)
            for i, chunk in enumerate(chunks)
        ]
        ids_lst = await asyncio.gather(*proms)
        # should i check for errors?
        return flatten_list(lst=ids_lst)
