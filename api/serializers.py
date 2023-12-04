from rest_framework import serializers

from rental.models import Setting

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = Setting
		fields = '__all__'
