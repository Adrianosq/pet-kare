from rest_framework.views import APIView, Request, Response, status
from pets.serializers import PetSerializer
from pets.models import Pet
from traits.models import Trait
from groups.models import Group
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


class PetView(APIView, PageNumberPagination):
    def post(self, request: Request) -> Response:

        serializer = PetSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop("group")
        traits = serializer.validated_data.pop("traits")

        group_obj = Group.objects.filter(
                scientific_name__iexact=group["scientific_name"]
            ).first()

        if not group_obj:
            group_obj = Group.objects.create(**group)

        pet_obj = Pet.objects.create(**serializer.validated_data, group=group_obj)

        for traits_dict in traits:
            traits_obj = Trait.objects.filter(
                name__iexact=traits_dict["name"]
            ).first()

            if not traits_obj:
                traits_obj = Trait.objects.create(**traits_dict)

            pet_obj.traits.add(traits_obj)

        serializer = PetSerializer(pet_obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:

        trait_params = request.query_params.get('trait', None)

        pets = Pet.objects.all()

        if trait_params:
            pets = Pet.objects.filter(
                traits__name=trait_params
            )

        result_page = self.paginate_queryset(pets, request)

        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)


class PetsDetailView(APIView):

    def get(self, request: Request, pet_id: int) -> Response:

        pet = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(pet)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, pet_id: int) -> Response:

        pet = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        traits: dict = serializer.validated_data.pop('traits', None)
        group: dict = serializer.validated_data.pop('group', None)

        if traits:
            for traits_dict in traits:
                traits_obj = Trait.objects.filter(
                    name__iexact=traits_dict["name"]
                ).first()

                if not traits_obj:
                    traits_obj = Trait.objects.create(**traits_dict)

                pet.traits.add(traits_obj)

        if group:
            group_obj = Group.objects.filter(
                scientific_name__iexact=group["scientific_name"]
            ).first()

            if not group_obj:
                group_obj = Group.objects.create(**group)

            pet.group = group_obj

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()

        serializer = PetSerializer(pet)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:

        pet = get_object_or_404(Pet, id=pet_id)

        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
