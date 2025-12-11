from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from stock.models import Stock

class Command(BaseCommand):
    help = 'Creates default groups and permissions'

    def handle(self, *args, **kwargs):
        # 1. Create Groups
        manager_group, created = Group.objects.get_or_create(name='Store Manager')
        staff_group, created = Group.objects.get_or_create(name='Staff')

        # 2. Get Permissions for the Stock model
        content_type = ContentType.objects.get_for_model(Stock)
        
        # Define permissions
        can_view = Permission.objects.get(codename='view_stock', content_type=content_type)
        can_add = Permission.objects.get(codename='add_stock', content_type=content_type)
        can_change = Permission.objects.get(codename='change_stock', content_type=content_type)
        can_delete = Permission.objects.get(codename='delete_stock', content_type=content_type)

        # 3. Assign Permissions to Groups
        # Manager gets everything
        manager_group.permissions.add(can_view, can_add, can_change, can_delete)
        
        # Staff can only View and Change (Issue/Receive updates the record)
        # Staff CANNOT Add new items or Delete existing ones
        staff_group.permissions.add(can_view, can_change)

        self.stdout.write(self.style.SUCCESS("Successfully created 'Store Manager' and 'Staff' groups!"))