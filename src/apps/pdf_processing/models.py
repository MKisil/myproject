import uuid

from django.db import models


class File(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    file = models.FileField(upload_to='pdf_processing/')
    time_add = models.DateTimeField(auto_now_add=True)
