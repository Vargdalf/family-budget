from rest_framework import serializers

from budgets.models import Budget, Category, Entry
from users.models import User


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ['category', 'name', 'amount']


class BudgetSerializer(serializers.ModelSerializer):
    entries = EntrySerializer(many=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    shared_with = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Budget
        fields = ['name', 'owner', 'entries', 'shared_with']

    def create(self, validated_data: dict) -> Budget:
        entries_data = validated_data.pop('entries')
        shared_with_data = validated_data.pop('shared_with')
        budget = Budget.objects.create(**validated_data)
        budget.shared_with.set(shared_with_data)
        for entry_data in entries_data:
            Entry.objects.create(budget=budget, **entry_data)
        return budget

    def update(self, instance: Budget, validated_data: dict) -> Budget:
        if 'entries' not in validated_data:
            return super().update(instance, validated_data)
        entries_data = validated_data.pop('entries')
        updated_instance: Budget = super().update(instance, validated_data)
        new_entries = [Entry.objects.create(budget=updated_instance, **entry_data) for entry_data in entries_data]
        updated_instance.entries.all().delete()
        for entry in new_entries:
            entry.save()
            updated_instance.entries.add(entry)
        return updated_instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']
