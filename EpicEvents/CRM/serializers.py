from rest_framework import serializers
from .models import UserWithRole, Client, Event, Contract, User

from rest_framework import serializers
from .models import UserWithRole


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserWithRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserWithRole
        fields = ['user', 'role']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        
        print(f'Updating user {user.id} with data {user_data}')

        # Update the User instance
        for field, value in user_data.items():
            setattr(user, field, value)
        user.save(update_fields=user_data.keys())

        # Update the UserWithRole instance
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save(update_fields=validated_data.keys())

        return instance

    def get_role(self, obj):
        return obj.get_role_display()


class ClientSerializer(serializers.ModelSerializer):
    associated_team_member = UserWithRoleSerializer(read_only=True)

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EventSerializer(serializers.ModelSerializer):
    # client = ClientSerializer(read_only=True)
    # associated_team_member = UserWithRoleSerializer(read_only=True)

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ContractSerializer(serializers.ModelSerializer):
    # event = EventSerializer(read_only=True)
    # client = ClientSerializer(read_only=True)
    # associated_team_member = UserWithRoleSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
