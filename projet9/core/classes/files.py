from pathlib import Path
from django.conf import settings

class HandleUploadedFile:
    def __init__(self, file, filename):
        self.file = file
        self.filename = filename
        if self._check_extension() is True:
            self.handle_uploaded_file()
        
    def _check_extension(self):
        allowed_extensions = ['.jpg', '.png']
        return True if Path(self.filename.lower()).suffixes[0] in allowed_extensions else False
        
    def handle_uploaded_file(self):
        fullpath = f'{settings.MEDIA_ROOT}{self.filename}'
        with open(fullpath, 'wb+') as destination:
            for chunk in self.file.chunks():
                destination.write(chunk)