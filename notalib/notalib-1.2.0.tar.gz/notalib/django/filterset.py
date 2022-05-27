from ..filterset import FilterSet, create_filter_set as cfs

from collections import namedtuple

from django.forms import Form


Result = namedtuple('Result', ['is_valid', 'errors', 'data'])

def create_filter_set(field_definitions: dict, required=None, parent=None):
	ret = cfs(field_definitions.keys(), required, parent)

	real_fd = field_definitions.copy()
	if parent != None:
		for key in parent._meta['field_definitions']:
			real_fd[key] = parent._meta['field_definitions'][key]

	DynamicFormInner = type('DynamicFormInner', (Form,), real_fd.copy())

	ret._meta = {}
	ret._meta['field_definitions'] = real_fd
	ret._meta['form'] = DynamicFormInner
	return ret

def from_request(FS: FilterSet, request_payload: dict) -> Result:
	fs = FS(**request_payload)

	form_payload = {}
	for f in fs._fields:
		if f in request_payload:
			form_payload[f] = request_payload[f]

	form = FS._meta['form'](form_payload)
	if form.is_valid():
		return Result(is_valid=True, errors=None, data=FS(**form.cleaned_data))
	else:
		return Result(is_valid=False, errors=form.errors, data=None)
