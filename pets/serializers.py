from rest_framework import serializers
from .models import CategoryPet
from traits.serializers import TraitSerializer
from groups.serializers import GroupSerializer


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(
        choices=CategoryPet.choices, default=CategoryPet.NOT_INFORMED
    )
    group = GroupSerializer()
    traits = TraitSerializer(many=True)
