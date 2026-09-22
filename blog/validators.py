from django.core.exceptions import ValidationError
import os

def validate_image_size(image):
    max_size_mb = 5
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'Image size cannot be more than {max_size_mb}MB.')

def validate_image_extension(image):
    valid_extensions = ['.jgep', 'jpg', '.png', '.webp', '.gif']
    extension = image.name.lower().split('.')[-1]
    if f'.{extension}' not in valid_extensions:
        raise ValidationError(f'Unsupported image format. Use: {valid_extensions}')