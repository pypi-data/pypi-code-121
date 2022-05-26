from vinca._card import Card
from vinca._browser import Browser
from vinca._lib import ansi
from vinca._lib.readkey import readkey
from vinca._lib.julianday import today
from vinca._statistics import Statistics

from rich import print

class Cardlist(list):
        """"""
        ''' A Cardlist is basically just an SQL query linked to a database
        The filter, sort, findall, and slice methods build up this query
        When used as an iterator it is just a list of cards (ids) 
        It is responsible for knowing its database, usually ~/cards.db '''

        def __init__(self, cursor, conditions=['TRUE'],
            ORDER_BY = ' ORDER BY (select max(date) from reviews where reviews.card_id=cards.id) DESC'):
                self._cursor = cursor   
                self._conditions = conditions
                self._ORDER_BY = ORDER_BY
                # we intentionally skip calling super().__init__ because we only are calling ourselves a list
                # so that Fire thinks we are one. We don't actually care about inheritance!

        # overwrite __dir__ so that we fool python FIRE
        # we don't want methods inherited from list
        # to show up in our help message
        def __dir__(self):
                members = super().__dir__()
                hidden = ['extend','index','pop','mro','remove','append',
                          'clear','insert','reverse','copy']
                return [m for m in members if m not in hidden]

        def _copy(self):
                # create a copy of the conditions list obejct (lists are mutable!)
                # we don't want to be affected by subsequent changes to conditions
                return self.__class__(
                        self._cursor,
                        self._conditions.copy(),
                        self._ORDER_BY)

        @property
        def _SELECT_IDS(self):
                """SQL Query of all card IDs. Check this first when debugging."""
                return 'SELECT id FROM cards' + self._WHERE + self._ORDER_BY

        @property
        def _WHERE(self):
                return ' WHERE ' + ' AND '.join(self._conditions)

        def explicit_cards_list(self, LIMIT = 1000):
                self._cursor.execute(self._SELECT_IDS + f' LIMIT {LIMIT}')
                ids = [row[0] for row in self._cursor.fetchall()]
                return [Card(id, self._cursor) for id in ids]

        def __getitem__(self, arg):
                # access cards by their index
                # we use human-oriented indexing beginning with 1...
                if type(arg) is slice:
                        idx = arg.stop 
                elif type(arg) is int:
                        idx = arg
                else:
                        raise ValueError
                self._cursor.execute(self._SELECT_IDS + f' LIMIT 1 OFFSET {idx - 1}')
                card_id = self._cursor.fetchone()[0]
                return Card(card_id, self._cursor)

        def __iter__(self):
                # iterating is discouraged
                # there is usually a better way to do what you want in sql
                # but sometimes this is quick and convenient
                return (self[i] for i in range(1, len(self) + 1))


        def __len__(self):
                self._cursor.execute(f'SELECT COUNT(*) FROM ({self._SELECT_IDS})')
                return self._cursor.fetchone()[0]

        def __str__(self):
                sample_cards = self.explicit_cards_list(LIMIT=6)
                l = len(self)
                s = 'No cards.' if not l else f'6 of {l}\n' if l>6 else ''
                s += ansi.codes['line_wrap_off']
                s += '\n'.join([str(card) for card in sample_cards])
                s += ansi.codes['line_wrap_on']
                return s

        def browse(self):
                """interactively manage you collection"""
                Browser(self.explicit_cards_list(), self._make_basic_card, self._make_verses_card).browse()

        def review(self):
                """review your cards"""
                due_cards = self.filter(due = True).explicit_cards_list()
                Browser(due_cards, self._make_basic_card, self._make_verses_card).review()

        def tag(self, *tags):
                """add tags to selected cards"""
                for tag in tags:
                        self._cursor.execute(f'INSERT INTO tags (card_id, tag)'
                            f'SELECT id, "{tag}" from CARDS' + self._WHERE)
                self._cursor.connection.commit()
                print(self._cursor.rowcount, 'tags added')
                                
        def remove_tag(self, tag):
                """remove a tag from cards """
                self._cursor.execute(f'DELETE FROM tags WHERE card_id IN'
                        f'({self._SELECT_IDS}) AND tag = ?', (tag,))
                self._cursor.connection.commit()
                print(self._cursor.rowcount, 'tags removed')

        def tags(self):
                """all tags in this cardlist """
                self._cursor.execute(f'SELECT tag FROM tags JOIN '
                    f'({self._SELECT_IDS}) ON tags.card_id=id GROUP BY tag')
                return [row[0] for row in self._cursor.fetchall()]

        def count(self):
                """simple summary statistics"""
                return {'total':  len(self),
                        'due':    len(self.filter(due=True)),
                        'new':    len(self.filter(new=True))}

        def filter(self, *,
                   tag = None,
                   created_after=None, created_before=None,
                   due_after=None, due_before=None,
                   deleted=None, due=None, new=None, verses=None,
                   contains_images=None,
                   invert=False):
                """filter the collection"""
                # The default values of None signify that we will not filter
                # by this predicate. For example, new=False means that we will
                # only show cards which are not new, but new=None means that
                # we will show all cards.

                TODAY = today() # today's juliandate as an int e.g. 2457035

                parameters_conditions = (
                        # tag
                        (tag, f"(SELECT true FROM tags WHERE card_id=cards.id AND tag='{tag}')"),
                        # date conditions
                        (created_after, f"create_date > {TODAY + (created_after or 0)}"),
                        (created_before, f"create_date < {TODAY + (created_before or 0)}"),
                        (due_after, f"due_date > {TODAY + (due_after or 0)}"),
                        (due_before, f"due_date < {TODAY + (due_before or 0)}"),
                        # boolean conditions
                        (due, f"due_date < {TODAY}"),
                        (deleted, f"deleted = 1"),
                        (verses, f"verses = 1"),
                        (new, f"due_date = create_date"),
                        (contains_images, "front_image IS NOT NULL OR back_image IS NOT NULL"),
                )

                # assert that at least one filter predicate has been specified
                if all([p is None for p,c in parameters_conditions]):
                        return '''Examples:
filter --due                    ` due cards                  
filter --due-before -7            overdue by more than a week
filter --contains-images          cards containing images                           
filter --tag TAG --invert         cards not containing TAG   

Read `filter --help` for a complete list of predicates'''

                new_cardlist = self._copy()
                for parameter, condition in parameters_conditions:
                        if parameter is not None:
                                n = 'NOT ' if invert ^ (parameter is False) else ''
                                new_cardlist._conditions.append(n + condition)
                return new_cardlist

        def find(self, pattern):
                """ return the first card containing a search pattern """
                try:
                        return self.findall(pattern).sort('seen')[1]
                except:
                        return f'no cards containing "{pattern}"'


        def findall(self, pattern):
                """ return all cards containing a search pattern """
                new_cardlist = self._copy()
                new_cardlist._conditions += [f"(front_text LIKE '%{pattern}%' \
                        OR back_text LIKE '%{pattern}%')"]
                return new_cardlist

        def sort(self, criterion=None, *, reverse=False):
                """ sort the collection: [due | seen | created | time | random] """
                # E.g. we want to see the cards that have taken the most time first
                        
                crit_dict = {'due': ' ORDER BY due_date',
                             'created': ' ORDER BY create_date',
                             'random': ' ORDER BY RANDOM()',
                             'time': ' ORDER BY (select sum(seconds) from reviews where reviews.card_id=cards.id)',
                             'seen': ' ORDER BY (select max(date) from reviews where reviews.card_id=cards.id)',
                              }
                if criterion not in crit_dict:
                        print(f'supply a criterion: {" | ".join(crit_dict.keys())}')
                        exit()
                new_cardlist = self._copy()
                new_cardlist._ORDER_BY = crit_dict[criterion]
                # Sometimes it is natural to see the highest value first by default
                reverse ^= criterion in ('created', 'seen', 'time') 
                direction = ' DESC' if reverse else ' ASC'
                new_cardlist._ORDER_BY += direction
                return new_cardlist
                
        def _make_basic_card(self):
                """ make a basic question and answer flashcard """
                card = Card._new_card(self._cursor)
                card.edit()
                return card
        basic = _make_basic_card

        def _make_verses_card(self):
                """ make a verses card: for recipes, poetry, oratory, instructions """
                card = Card._new_card(self._cursor)
                card.verses = True
                card.edit()
                return card
        verses = _make_verses_card

        def delete(self):
                print(f'[bold]delete {len(self)} cards? y/n')
                if readkey() != 'y':
                        print('[red]aborted')
                        return
                self._cursor.execute(f'UPDATE cards SET deleted = 1' + self._WHERE)
                self._cursor.connection.commit()
                print(len(self), 'cards deleted')

        def restore(self):
                deleted_cards = self.filter(deleted=True)
                if len(deleted_cards) == 0:
                        print('none of these cards are deleted')
                self._cursor.execute(f'UPDATE cards SET deleted = 0' + deleted_cards._WHERE)
                self._cursor.connection.commit()
                print(self._cursor.rowcount, 'cards restored')

        def purge(self):
                """ permanently remove deleted cards """
                deleted_cards = self.filter(deleted=True)
                n = len(deleted_cards)
                if n == 0:
                        print('no cards to delete')
                        return
                print(f'[bold]permanently remove {len(deleted_cards)} cards?! y/n')
                if readkey() != 'y':
                        print('[red]aborted')
                        return
                # PRAGMA... enables foreign key delete cascade
                # When a card is deleted so are its associated tags and reviews
                deleted_cards._cursor.execute("PRAGMA FOREIGN_KEYS = on;")
                deleted_cards._cursor.execute("DELETE FROM cards" + deleted_cards._WHERE)
                print(f'{deleted_cards._cursor.rowcount} cards purged')
                deleted_cards._cursor.connection.commit()

        def stats(self, interval=7):
                """ review statistics for the collection """
                return Statistics(self._cursor, interval=interval).print()
