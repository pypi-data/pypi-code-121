from .filterset import create_filter_set

import pytest


def test_filter_set():
	CountryFilterSet = create_filter_set(['country'], required=['country'])
	AddressFilterSet = create_filter_set(['city', 'street'], required=['city'], parent=CountryFilterSet)

	with pytest.raises(AssertionError): CountryFilterSet()
	_ = CountryFilterSet(country='Russia')
	with pytest.raises(AssertionError): AddressFilterSet()
	with pytest.raises(AssertionError): AddressFilterSet(country='Russia')
	_ = AddressFilterSet(country='Russia', city='Penza')

	source = {
		'country': 'Russia',
		'city': 'Penza',
		'street': 'Something st.',
	}
	fs = AddressFilterSet(**source)

	for key in source:
		with pytest.raises(AssertionError):
			getattr(fs, key)

	with pytest.raises(AssertionError): fs.unfreeze([])
	with pytest.raises(AssertionError): fs.unfreeze(['country'])
	with pytest.raises(AssertionError): fs.unfreeze(['country', 'city'])

	fs.unfreeze(['country', 'city', 'street'])

	assert fs.as_dict() == source

	for key in source:
		assert getattr(fs, key) == source[key]

	### apply

	def do_nothing(*args, **kwargs): pass

	with pytest.raises(AssertionError): fs.apply({})
	with pytest.raises(AssertionError): fs.apply({'country': do_nothing})
	with pytest.raises(AssertionError): fs.apply({'country': do_nothing, 'city': do_nothing})

	class SomeMock:
		called_times = 0
		def assert_country(self, value):
			assert value == 'Russia'
			self.called_times += 1
		def assert_city(self, value):
			assert value == 'Penza'
			self.called_times += 1
		def assert_street(self, value):
			assert value == 'Something st.'
			self.called_times += 1
	tfa = SomeMock()

	fs.apply({
		'country': lambda f, value: tfa.assert_country(value),
		'city': lambda f, value: tfa.assert_city(value),
		'street': lambda f, value: tfa.assert_street(value),
	})
	assert tfa.called_times == 3
