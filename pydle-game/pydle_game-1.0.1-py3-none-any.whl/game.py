import json
import logging
import random
from collections import Counter
from pathlib import Path
from typing import List, Optional, Tuple, Union

from rich.prompt import Prompt
from rich import print


_logger = logging.getLogger(__name__)

FilePath = Union[str, Path]


class Pydle:
    def __init__(self, word_file: Optional[FilePath] = None):
        _default_word_file = Path(__file__).parent.absolute() / "data" / "words.json"
        # Give the option for a user to supply a json list of words
        # Otherwise use our default list
        word_file = Path(word_file) if word_file else _default_word_file
        _logger.info("Word file being used is %s", str(word_file.absolute()))
        if not word_file.exists():
            _logger.error("Word file %s does not exist", str(word_file))
            raise FileNotFoundError(str(word_file))

        self._word_options: List[str] = self.get_word_options(word_file)
        self._word_choice: str = self._select_word()
        self._word_length: int = 5
        self._guess: str = ""

    @staticmethod
    def get_word_options(word_file: Path) -> List[str]:
        with word_file.open("rt") as f:
            words = json.load(f)
        return words

    def _select_word(self) -> str:
        return random.choice(self._word_options)

    def get_user_guess(self, remaining: int = None) -> str:
        self._guess = Prompt.ask(
            f"\n\n[gray]Guess{f' ({remaining} remaining)' if remaining else ''}[/gray]"
        ).strip()
        if len(self._guess) != self._word_length:
            print(f"[red]ERROR: Guess must be a {self._word_length} letter word[/red]")
            self.get_user_guess(remaining=remaining)
        if self._guess not in self._word_options:
            print(f"[red]ERROR: Guess is not actually a word!.[/red]")
            self.get_user_guess(remaining=remaining)
        return self._guess

    def process_user_guess(self) -> Tuple[bool, List[dict]]:
        answer_letters = list(self._word_choice)
        answer_count = Counter(answer_letters)
        guess_letters = list(self._guess)

        guess_info = []
        print(self._word_choice)
        for guess, answer in zip(guess_letters, answer_letters):
            letter_info = {"letter": guess, "color": "grey84"}
            if guess == answer:
                letter_info["color"] = "spring_green2"
                answer_count[guess] -= 1
            guess_info.append(letter_info)

        for i, square in enumerate(guess_info):
            letter = square["letter"]
            if letter in answer_letters:
                if answer_count[letter] > 0:
                    guess_info[i]["color"] = "yellow3"
                    answer_count[letter] -= 1

        return self._is_correct(), guess_info

    def _is_correct(self):
        return self._word_choice == self._guess


if __name__ == "__main__":
    print("This is not the py you seek")
