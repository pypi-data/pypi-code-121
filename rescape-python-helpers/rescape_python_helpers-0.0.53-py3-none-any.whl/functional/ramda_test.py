from pyramda import map_dict
from snapshottest import TestCase

from rescape_python_helpers.functional.ramda import to_dict_deep, all_pass_dict, flatten_dct, map_keys_deep, \
    map_with_obj_deep, pick_deep, unflatten_dct, fake_lens_path_view, key_string_to_lens_path, props, \
    fake_lens_path_set, index_by, props_or, str_paths_or, chain_with_obj_to_values, one_unique_or_raise, \
    flatten_dct_until, pick, unique_by, pick_deep_all_array_items, prop, find_all_deep, prop_or, when, replace_all_deep, \
    merge, index_by_and_map_items
from . import ramda as R


def unflatten_obj(flat_dct):
    pass


class TestRamda(TestCase):

    def test_filter_dict(self):
        dct = R.filter_dict(lambda keyvalue: keyvalue[0] == 'a', dict(a=1, b=2))
        assert dct == dict(a=1)

    def test_all_pass_dict(self):
        assert all_pass_dict(lambda k, v: v, dict(a=1, b=1))
        assert not all_pass_dict(lambda k, v: v, dict(a=1, b=None))
        assert not all_pass_dict(lambda k, v: v == 2, dict(a=1, b=1))

    def test_map_prop_value_as_index(self):
        res = R.map_prop_value_as_index(
            'province',
            [
                dict(province="Alberta"),
                dict(province="Manitoba")
            ]
        )
        assert res == dict(Alberta=dict(province="Alberta"), Manitoba=dict(province="Manitoba"))

    def test_item_path_or(self):
        assert R.item_path_or('racehorse', ['one', 'one', 'was'], dict(one=dict(one=dict(was='a')))) == 'a'
        assert R.item_path_or('racehorse', ['one', 'one', 'is'], dict(one=dict(one=dict(was='a')))) == 'racehorse'
        assert R.item_path_or('racehorse', 'one.one.was', dict(one=dict(one=dict(was='a')))) == 'a'

        # Try with a mix of dict and obj
        class Fellow(object):
            def __init__(self, one):
                self.one = one

        assert R.item_path_or('racehorse', 'one.one.was', dict(one=Fellow(one=dict(was='a')))) == 'a'

    def test_omit_deep(self):
        omit_keys = ['foo', 'bar']
        dct = dict(marty={}, foo=1, bar=2,
                   car=dict(foo=3, bar=4, tar=5, pepper=[[dict(achoo=1, bar=2), dict(kale=1, foo=2)]]))
        assert R.omit_deep(omit_keys, dct) == dict(marty={}, car=dict(tar=5, pepper=[[dict(achoo=1), dict(kale=1)]]))

    def test_find_all_deep(self):
        predicate = prop_or(False, 'id')
        dct = dict(jimmy=dict(id=1, dock=dict(tock=dict(id=2), mim=[]),
                              jam=dict(id=3, beverly=dict(sam=[dict(id=4), dict(ken=dict(id=5))]))))
        assert len(find_all_deep(predicate, dct)) == 5
        assert list(map(prop('id'), find_all_deep(predicate, dct))) == [1, 2, 3, 4, 5]

    def test_replace_all_deep(self):
        def mapping_func(key, value):
            return when(
                lambda key_value: prop_or(False, 'id', key_value[1]) if isinstance(key_value[1], dict) else False,
                lambda key_value: [f'{key_value[0]}Super', merge(key_value[1], dict(great=key_value[1]['id']))]
            )([key,value])

        dct = dict(jimmy=dict(id=1, dock=dict(tock=dict(id=2), mim=[]),
                              jam=dict(id=3, beverly=dict(sam=[dict(id=4), dict(ken=dict(id=5))]))))
        assert replace_all_deep(mapping_func, dct)['jimmySuper']['jamSuper']['beverly']['sam'][1]['kenSuper']['great'] == 5

    def test_pick(self):
        class Paddy(object):
            def __init__(self, one, two):
                self.one = one
                self.two = two

        assert pick(['a', 'b'], dict(a=1, c='cow')) == dict(a=1)
        assert pick(['one', 'three'], Paddy(one=1, two=2)) == dict(one=1)

    def test_pick_deep(self):
        pick_out = dict(
            billy=dict(goat=['takes', 'a', 'bite'], of=dict(tire=True, shoe={}, popsicle=None)),
            coat=True,
        )
        assert pick_deep(
            pick_out,
            dict(
                billy=dict(goat=['takes', 'a', 'kite'],
                           of=dict(tire=True, shoe=dict(default='left'), fruit=None, popsicle='Sweet')),
                coat=dict(_and=['jacket']),
                andthe=dict(cow=['jumps', 'over', 'the', 'coon'])
            )
        ) == dict(
            billy=dict(goat=['takes', 'a', 'kite'],
                       of=dict(tire=True, shoe={}, popsicle='Sweet')),
            coat=dict(_and=['jacket'])
        )

    def test_pick_deep_all_array_items(self):
        pick_out = dict(
            billy=dict(goat=['takes'], of=dict(tire=True, shoe={}, popsicle=None)),
            coat=True,
        )
        assert pick_deep_all_array_items(
            pick_out,
            dict(
                billy=dict(goat=['takes', 'a', 'kite'],
                           of=dict(tire=True, shoe=dict(default='left'), fruit=None, popsicle='Sweet')),
                coat=dict(_and=['jacket']),
                andthe=dict(cow=['jumps', 'over', 'the', 'coon'])
            )
        ) == dict(
            billy=dict(goat=['takes', 'a', 'kite'],
                       of=dict(tire=True, shoe={}, popsicle='Sweet')),
            coat=dict(_and=['jacket'])
        )

    def test_filter_deep(self):
        # This should pass
        params1 = dict(
            foo=1,
            car=dict(foo=3)
        )
        # This should fail
        params2 = dict(
            foo=1,
            car=dict(tool=3)
        )
        # This should pass
        params3 = dict(
        )
        # This should pass
        params4 = dict(
            car=dict(
                pepper=[
                    [
                        dict(achoo=1),
                        dict(kale=1)
                    ]
                ]
            )
        )
        # This should fail
        params5 = dict(
            car=dict(
                pepper=[
                    [
                        dict(achoo=1),
                        dict(kale=1),
                        dict(shoe=1)
                    ]
                ]
            )
        )

        dct = dict(
            foo=1,
            bar=2,
            car=dict(
                foo=3,
                bar=4,
                tar=5,
                pepper=[
                    [
                        dict(achoo=1, bar=2),
                        dict(kale=1, foo=2)]
                ]
            )
        )
        assert R.dict_matches_params_deep(params1, dct)
        assert not R.dict_matches_params_deep(params2, dct)
        assert R.dict_matches_params_deep(params3, dct)
        assert R.dict_matches_params_deep(params4, dct)
        assert not R.dict_matches_params_deep(params5, dct)

    def test_prop(self):
        assert R.prop('obazda', dict(obazda='dip')) == 'dip'

        # Try with a mix of dict and obj
        class Radish(object):
            def __init__(self, cut):
                self.garnish = cut

        assert R.prop('garnish', Radish('spiraled')) == 'spiraled'

    def test_merge_deep_all(self):
        assert R.merge_deep_all([
            dict(a=1, zoo=dict(a=2, b=2)),
            dict(a=2, zoo=dict(a=3, c=4, pen=dict(bull=False)), nursery=[1]),
            dict(zoo=dict(d=4, e=4, pen=dict(cow=True)), nursery=[2]),
        ]) == dict(
            a=2,
            zoo=dict(a=3, b=2, c=4, d=4, e=4, pen=dict(bull=False, cow=True)),
            nursery=[1, 2]
        )

    def test_to_dict_deep(self):
        class Beobazte(object):
            def __init__(self):
                self.cream = 'yummy'

        class Radish(object):
            def __init__(self, cut):
                self.garnish = Beobazte()
                self.cut = cut

        assert to_dict_deep(Radish('spiraled')) == dict(garnish=dict(cream='yummy'), cut='spiraled')

    def test_flatten_dct(self):
        result = flatten_dct(
            dict(iss=dict(there=dict(anybody=['willing', 'to'], listen=[dict(to='my'), 'story']))),
            '__'
        )
        assert {'iss__there__anybody__0': 'willing',
                'iss__there__anybody__1': 'to',
                'iss__there__listen__0__to': 'my',
                'iss__there__listen__1': 'story'
                } == result

    def test_unflatten_dct(self):
        dct = dict(iss=dict(there=dict(anybody=['willing', 'to'], listen=[dict(to='my'), 'story'])))
        flat_dct = flatten_dct(dct, '.')
        assert dct == unflatten_dct(flat_dct)

    def test_map_with_obj_deep(self):
        assert map_with_obj_deep(
            lambda k, v: [f'{v}Cool' if isinstance(v, str) else v],
            dict(
                a=dict(
                    b=[
                        'c',
                        dict(
                            d='f'
                        )
                    ]
                )
            )
        ) == {'a': [
            {'b': [
                [
                    ['cCool'],
                    [
                        {'d':
                            [
                                'fCool'
                            ]
                        }
                    ],
                ]
            ]
            }
        ]
               }

    def test_map_keys_deep(self):
        assert map_keys_deep(
            lambda k, v: f'{k}Cool' if isinstance(k, str) else k,
            dict(
                a=dict(
                    b=[
                        'c',
                        dict(
                            d='f'
                        )
                    ]
                )
            )
        ) == {'aCool': {'bCool': ['c', {'dCool': 'f'}]}}

    def test_fake_lens_path_view(self):
        result = fake_lens_path_view(key_string_to_lens_path('cherry.strawberry.orange'), dict(
            cherry=dict(
                strawberry=dict(
                    orange='pretzel'
                )
            )
        ))
        assert result == 'pretzel'

    def test_fake_lens_path_set(self):
        result = fake_lens_path_set(key_string_to_lens_path('cherry.strawberry.orange'), 'buddy holly', dict(
            cherry=dict(
                strawberry=dict(
                    orange='pretzel'
                )
            )
        ))
        assert result == dict(
            cherry=dict(
                strawberry=dict(
                    orange='buddy holly'
                )
            )
        )

        class Junior(object):
            def __init__(self, one):
                self.cherry = one

        zob = fake_lens_path_set(key_string_to_lens_path('cherry.strawberry.orange'), 'buddy holly', Junior(dict(
            strawberry=dict(
                orange='pretzel'
            )
        )))
        assert zob.__dict__ == Junior(dict(
            strawberry=dict(
                orange='buddy holly'
            )
        )).__dict__

    def test_props(self):
        result = props(['myr', 'beite', 'seter'], dict(myr='soggy', beite='tasty', seter='sleepy', avfall='dirty'))
        assert result == ['soggy', 'tasty', 'sleepy']

    def test_props_or(self):
        result = props_or('undefined', ['myr', 'smook', 'beite', 'seter'],
                          dict(myr=None, beite='tasty', seter='sleepy', avfall='dirty'))
        assert result == [None, 'undefined', 'tasty', 'sleepy']

    def test_str_paths_or(self):
        result = str_paths_or(
            'undefined',
            ['panda.myr', 'smook', 'panda.beite', 'panda.seter', 'avfall', 'panda.george.2.1'],
            dict(panda=dict(myr=None, beite='tasty', seter='sleepy', george=[0, 1, [0, 2]]), avfall='dirty')
        )
        assert result == [None, 'undefined', 'tasty', 'sleepy', 'dirty', 2]

    def test_index_by(self):
        assert index_by(
            R.prop('topping'),
            [
                dict(apple='pie', topping='ice cream'),
                dict(apple='tort', topping='ice cream'),
                dict(apple='cider', topping='nutmeg'),
                dict(apple='snapps', topping='nutmeg'),
                dict(apple='vinegar', topping='none'),
                dict(apple='jacks', topping='milk'),
            ]
        ) == {
                   'ice cream': [
                       dict(apple='pie', topping='ice cream'),
                       dict(apple='tort', topping='ice cream')
                   ],
                   'nutmeg': [
                       dict(apple='cider', topping='nutmeg'),
                       dict(apple='snapps', topping='nutmeg')
                   ],
                   'none': [
                       dict(apple='vinegar', topping='none'),
                   ],
                   'milk': [
                       dict(apple='jacks', topping='milk')
                   ]
               }

    def test_index_by_and_map_items(self):
        assert index_by_and_map_items(
            R.prop('topping'),
            R.omit(['topping']),
            [
                dict(apple='pie', topping='ice cream'),
                dict(apple='tort', topping='ice cream'),
                dict(apple='cider', topping='nutmeg'),
                dict(apple='snapps', topping='nutmeg'),
                dict(apple='vinegar', topping='none'),
                dict(apple='jacks', topping='milk'),
            ]
        ) == {
                   'ice cream': [
                       dict(apple='pie'),
                       dict(apple='tort')
                   ],
                   'nutmeg': [
                       dict(apple='cider'),
                       dict(apple='snapps')
                   ],
                   'none': [
                       dict(apple='vinegar'),
                   ],
                   'milk': [
                       dict(apple='jacks')
                   ]
               }

    def test_chain_with_obj_to_values(self):
        assert chain_with_obj_to_values(lambda k, v: R.map(lambda i: R.concat(k, str(i)), v),
                                        dict(a=[1, 2], b=[3, 4])) == ['a1', 'a2', 'b3', 'b4']

    def test_one_unique_or_raise(self):
        assert one_unique_or_raise(['Bah', 'Bah', 'Bah']) == 'Bah'

    def test_flatten_dct_until(self):
        dct = {'data': {'streets': ['Somehood']}}

        def test(key, value):
            return not R.isinstance(list, value) and not key.endswith('contains')

        assert flatten_dct_until(
            dct,
            test,
            '__'
        ) == {'data__streets': ['Somehood']}

    def test_unique_by(self):
        objs = [{'question': 'ask'},
                {'question': 'me'},
                {'question': 'if'},
                {'question': 'Im'},
                {'question': 'an'},
                {'question': 'apple'},
                {'question': 'an'},
                {'question': 'apple'},
                {'question': 'ask'},
                {'question': 'if'},
                {'question': 'Im'},
                {'question': 'me'}
                ]
        assert R.length(unique_by(R.prop('question'), objs)) == 6
