from pathlib import Path
from django.conf import settings
import uuid
import os


class HandleUploadedFile:
    def __init__(self, file=[], filename=""):
        self.file = file
        self.filename = filename

    def _check_extension(self):
        allowed_extensions = [".jpg", ".png"]
        return (
            True
            if Path(self.filename.lower()).suffixes[0] in allowed_extensions
            else False
        )

    def _get_uuid_filename(self):
        return f"{str(uuid.uuid4())}{Path(self.filename.lower()).suffix}"

    def upload(self):
        if self._check_extension() is True:
            self.filename = self._get_uuid_filename()
            fullpath = f"{settings.MEDIA_ROOT}{self.filename}"
            with open(fullpath, "wb+") as destination:
                for chunk in self.file.chunks():
                    destination.write(chunk)

    def delete(self):
        file_path = Path(f"{settings.MEDIA_ROOT}{self.filename}")
        if file_path.is_file():
            os.remove(file_path)

    def get_filename(self):
        return self.filename
