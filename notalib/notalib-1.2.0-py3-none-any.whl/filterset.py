class FilterSet:
	"""
	Don't use this class directly, use create_filter_set instead.
	"""
	# Fields will be initialized by create_filter_set
	_fields = None
	_required = None
	_parent = None
	_meta = None  # for external use
	_frozen = True

	def __init__(self, **kwargs):
		for f in self._required:
			assert (f in kwargs), f"Field `{f}` is mandatory"
		for key in kwargs:
			assert key in self._fields, f"Unknown field `{key}`"
		self.values = kwargs

	def __getattr__(self, name: str):
		if name in self.__dict__:
			return self.__dict__[name]

		assert (not self._frozen), "FilterSet is frozen"
		return self.values[name]

	def unfreeze(self, expected_fields):
		assert sorted(expected_fields) == sorted(self._fields), f"Field set mismatch, expected: {self._fields}"
		self._frozen = False
		return self

	def as_dict(self):
		return self.values.copy()

	def apply(self, handlers):
		"""
		A piece of code that wants to use these filters calls FilterSet.apply()
		with a dict describing how to handle each field:

			qs = Address.objects.all()
			fs.apply({
				'country': lambda value: qs.filter(country=value),
				'city': lambda value: qs.filter(city=value),
			})

		Code MUST provide a handler for every field. If it does not, an exception
		is risen. So, if you ever add a new field, your implementations can't
		just forget to process that field unless you add a handler.

		Every callback is guaranteed to be called only once per apply() call.

		Hint: Making different implementations for one FilterSet is where it shines.
		"""
		assert (not self._frozen), "FilterSet is frozen"
		for field_name in self._fields:
			assert (field_name in handlers), f"FilterSet.apply: no implementation found for `{field_name}`"
			handlers[field_name](field_name, self.values[field_name])


def create_filter_set(fields, required=None, parent=None):
	"""
	FilterSet defines a set of filters that can be applied to some data.
	It's useful on its own, and it's a powerful abstraction for bigger projects.

	1. Definition.

	FilterSet defines some fields that can be used for filtering data.
	They must have valid Python names.

		AddressFilterSet = create_filter_set(['country', 'city'], required=['country'], parent=None)

	FilterSet is chainable. A child inherits all fields of every of its parents.

	2. Instantiation.

	FilterSet accepts kwargs for known field names.

		fs = AddressFilterSet(country='Russia', city='Penza')

	3. Application.

	FilterSet must be unfrozen before the code is allowed to look inside.
	(This method returns self.)

		fs.unfreeze(['country', 'city'])

	If the set of fields does not match FilterSet's set of field, an exception
	is raised.

		print(fs.country)
		print(fs.as_dict())

	---
	Так, представляю тебе новую суперкрутую вещь в pyutil. Называется FilterSet.
	Вот скажи: у тебя бывало такое, что надо в GET- или там POST-запросе принять какие-то параметры и по ним выдать отфильтрованный сет каких-нибудь данных?
	Ну ладно, это, наверное, у всех было.
	А вот бывало такое, что данные абсолютно разные, но фильтры у них одинаковые или по крайней мере имеют общие части?
	Ну типа, допустим, есть у тебя какая-нибудь админка с заказами и отзывами, но и те, и те фильтруются по дате, стране и городу.
	То есть, получается, ты пишешь и там, и там более-менее примерно одинаковый код, который берёт request, вытаскивает из него date, country и city и строит по ним QuerySet с данными.
	Абстрагироваться там как-то всё-таки трудно, потому что модели могут отличаться, ну и сами фильтры разные.
	Вот, а потом ещё иногда случается такое, что добавляется какой-то новый фильтр во все API - ну, например, помимо города ещё и район.
	И в этот момент происходит страшное: большинство реализаций будут просто игнорировать новое поле. Хотя оно важное. Они не просто сломаются, они будут работать, но возвращать не те данные, которые надо. Это вообще пиздец, хуже даже придумать что-то сложно.
	Единственное лекарство - очень долго и муторно отсматривать всё руками в таких случаях.
	Ну или тесты писать, но там та же проблема: надо не забыть покрыть нужными тестами все нужные API, а когда их много, что-нибудь да пропустишь.
	И ты думаешь: вот бы была какая-нибудь такая фигня, чтобы эти фильтры можно было обновить в одном месте и чтобы весь код, который не знает про новое поле, сразу нахуй сломался и его было видно.
	Дамы и господа, представляю вам FilterSet.
	С ним всё становится просто. Берёшь, описываешь чё у вас там в проекте есть:

		DeliveryFilterSet = create_filter_set({
			'area': formplus.IntegerArrayField(required=False, empty_value=None),
			'executor': formplus.StringArrayField(required=False, empty_value=None),
			'date_from': formplus.MonthField(required=False, empty_value=None),
			'date_to': formplus.MonthField(required=False, empty_value=None),
		})

	Если для конкретной вьюхи какие-то ещё параметры помимо глобальных есть, просто берёшь и пишешь об этом:

		@action(detail=False, methods=['get'])
		def stats(self, request):
			fs = create_filter_set({
				'group_by': formplus.ChoiceWithDefault(required=False, default='day', choices=(('day', 'day'), ('month', 'month'))),
			}, parent=DeliveryFilterSet)

	Разумеется, их можно вкладывать на любую глубину.
	Разумеется, библиотека за тебя всё провалидирует и даже сделает машиночитаемые отчёты об ошибках, которые останется просто отдать клиенту:

		parsed = from_request(fs, request.GET)
		if not parsed.is_valid:
			return Response(parsed.errors.as_data(), status=status.HTTP_400_BAD_REQUEST)

	Ну и магия. Перед использованием FilterSet надо разморозить, указав, какие поля ты собираешься оттуда читать. Если код ещё не знает про новое поле - он сразу посылается нахуй:

	data = parsed.data.unfreeze(['area', 'executor', 'date_from', 'date_to', 'group_by']).as_dict()

	После этого остаётся только найти все красные тесты и пофиксить их. Пропустить что-то невозможно. Легко? Невероятно легко.
	Оформляйте предзаказ всего за 99.99$
	"""

	ret_fields = []
	ret_required = []
	ret_parent = parent

	# Copy things from parent if needed
	if parent != None:
		for f in parent._fields:
			ret_fields.append(f)
		for f in parent._required:
			ret_required.append(f)

	for f in fields:
		ret_fields.append(f)
	if required != None:
		for f in required:
			ret_required.append(f)

	class FilterSetInstance(FilterSet):
		_fields = ret_fields
		_required = ret_required
		_parent = ret_parent
	return FilterSetInstance
