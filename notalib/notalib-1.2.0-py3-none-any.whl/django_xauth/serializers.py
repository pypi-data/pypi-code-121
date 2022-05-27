from .models import Nothing

from rest_framework import serializers


class NothingSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Nothing
		fields = ()
