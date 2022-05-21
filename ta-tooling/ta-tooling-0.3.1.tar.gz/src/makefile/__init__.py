import re


class Target:
    """
    A target in a Makefile.
    """

    def __init__(self, name, dependencies, statements):
        self.name = name.strip()
        self.dependencies = dependencies.strip().split(" ")
        self.statements = [s.strip() for s in statements]

    def __str__(self):
        return f"{self.name}: {self.dependencies}"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_lines(cls, lines):
        """
        Create target from string.
        """
        tokens = lines[0].split(":")
        if len(tokens) == 2:
            name, dependencies = tokens
        else:
            name, dependencies = tokens[0], ""
        return cls(name, dependencies, lines[1:])

    def is_depend_on(self, depens):
        return all([d in self.dependencies for d in depens])

    def depend_is(self, depens):
        return set(self.dependencies) == set(depens)


class Makefile:
    """
    A Makefile.
    """

    target_pattern = re.compile(r"^(?P<targetname>.+:)")
    statement_pattern = re.compile(r"^\t.+")

    def __init__(self, path):
        self.path = path
        self.lines = []
        self.targets = []

        self.read()
        self.parse()

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError("key has to be string")

        for t in self.targets:
            if t.name == key:
                return t
        raise KeyError(f"{key} cannot be found")

    def read(self):
        with open(self.path, "r") as f:
            self.lines = f.readlines()

    def parse(self):
        targets = []
        target_lines = []

        for line in self.lines:
            target_match_result = self.target_pattern.search(line)
            statement_match_result = self.statement_pattern.match(line)

            if target_match_result is not None:
                if len(target_lines) != 0:
                    targets.append(Target.from_lines(target_lines))
                target_lines = [line]
            elif statement_match_result is not None:
                target_lines.append(line)
        # That one last target.
        if len(target_lines) != 0:
            targets.append(Target.from_lines(target_lines))

        self.targets = targets
