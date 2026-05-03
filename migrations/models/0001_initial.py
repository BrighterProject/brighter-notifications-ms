from tortoise import migrations
from tortoise.migrations import operations as ops
from app.models import NotificationChannel, NotificationStatus
from uuid import uuid4
from tortoise import fields

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='Notification',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('channel', fields.CharEnumField(default=NotificationChannel.EMAIL, description='EMAIL: email', enum_type=NotificationChannel, max_length=5)),
                ('recipient', fields.CharField(max_length=255)),
                ('subject', fields.CharField(max_length=500)),
                ('template', fields.CharField(max_length=100)),
                ('status', fields.CharEnumField(default=NotificationStatus.SENT, description='SENT: sent\nFAILED: failed', enum_type=NotificationStatus, max_length=6)),
                ('resend_id', fields.CharField(null=True, max_length=255)),
                ('error', fields.TextField(null=True, unique=False)),
                ('triggered_by', fields.CharField(null=True, max_length=100)),
            ],
            options={'table': 'notifications', 'app': 'models', 'pk_attr': 'id'},
            bases=['AbstractModel'],
        ),
    ]
