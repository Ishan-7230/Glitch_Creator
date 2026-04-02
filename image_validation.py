"""
Image Validation Module for Security
Validates uploaded images to prevent security vulnerabilities including:
- Malicious file uploads
- File type spoofing
- Memory exhaustion attacks
- Invalid image formats
"""

import io
from PIL import Image
from PIL import UnidentifiedImageError
import struct


class ImageValidationError(Exception):
    """Custom exception for image validation errors"""
    pass


class ImageValidator:
    """
    Comprehensive image validator with multiple security checks.
    """
    
    # Maximum file size: 20MB (adjustable)
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    
    # Maximum image dimensions: 10000x10000 pixels
    MAX_DIMENSION = 10000
    
    # Minimum image dimensions: 1x1 pixels
    MIN_DIMENSION = 1
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'image/jpeg',
        'image/jpg',
        'image/png'
    }
    
    # Magic bytes for image formats (first few bytes of file)
    MAGIC_BYTES = {
        b'\xff\xd8\xff': 'JPEG',  # JPEG files start with FF D8 FF
        b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': 'PNG',  # PNG files start with 89 50 4E 47
    }
    
    @staticmethod
    def validate_file_extension(filename):
        """
        Validates file extension against allowed types.
        
        Args:
            filename: Name of the uploaded file
            
        Returns:
            bool: True if extension is valid
            
        Raises:
            ImageValidationError: If extension is invalid
        """
        if not filename:
            raise ImageValidationError("Filename is empty")
        
        allowed_extensions = {'.jpg', '.jpeg', '.png'}
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if not file_ext or f'.{file_ext}' not in allowed_extensions:
            raise ImageValidationError(
                f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return True
    
    @staticmethod
    def validate_file_size(file_data):
        """
        Validates file size to prevent memory exhaustion attacks.
        
        Args:
            file_data: File data (bytes or file-like object)
            
        Returns:
            bool: True if size is valid
            
        Raises:
            ImageValidationError: If file is too large
        """
        if hasattr(file_data, 'read'):
            # File-like object (Streamlit UploadedFile)
            file_data.seek(0, 2)  # Seek to end
            size = file_data.tell()
            file_data.seek(0)  # Reset to beginning
        else:
            # Bytes object
            size = len(file_data)
        
        if size > ImageValidator.MAX_FILE_SIZE:
            max_mb = ImageValidator.MAX_FILE_SIZE / (1024 * 1024)
            raise ImageValidationError(
                f"File size ({size / (1024 * 1024):.2f} MB) exceeds maximum "
                f"allowed size ({max_mb} MB)"
            )
        
        if size == 0:
            raise ImageValidationError("File is empty")
        
        return True
    
    @staticmethod
    def validate_magic_bytes(file_data):
        """
        Validates file content using magic bytes (file signature).
        This prevents file type spoofing attacks.
        
        Args:
            file_data: File data (bytes or file-like object)
            
        Returns:
            str: Detected image format
            
        Raises:
            ImageValidationError: If magic bytes don't match expected formats
        """
        # Read first 16 bytes for magic byte detection
        if hasattr(file_data, 'read'):
            # File-like object
            current_pos = file_data.tell()
            file_data.seek(0)
            header = file_data.read(16)
            file_data.seek(current_pos)  # Restore position
        else:
            # Bytes object
            header = file_data[:16]
        
        if len(header) < 8:
            raise ImageValidationError("File too small to be a valid image")
        
        # Check magic bytes
        detected_format = None
        
        # Check JPEG (starts with FF D8 FF)
        if header[:3] == b'\xff\xd8\xff':
            detected_format = 'JPEG'
        # Check PNG (starts with 89 50 4E 47 0D 0A 1A 0A)
        elif header[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
            detected_format = 'PNG'
        else:
            raise ImageValidationError(
                "Invalid file signature. File does not appear to be a valid JPEG or PNG image. "
                "This may be a malicious file disguised as an image."
            )
        
        return detected_format
    
    @staticmethod
    def validate_image_content(file_data):
        """
        Validates image content using PIL to ensure it's a valid image.
        This is the most important check as it actually tries to decode the image.
        
        Args:
            file_data: File data (bytes or file-like object)
            
        Returns:
            PIL.Image.Image: Validated PIL Image object
            
        Raises:
            ImageValidationError: If image cannot be opened or is invalid
        """
        try:
            # Ensure we're at the beginning if it's a file-like object
            if hasattr(file_data, 'seek'):
                file_data.seek(0)
            
            # Attempt to open and verify the image
            image = Image.open(file_data)
            
            # Verify the image can be loaded (lazy loading check)
            image.verify()
            
            # Reopen after verify (verify() closes the image)
            if hasattr(file_data, 'seek'):
                file_data.seek(0)
            image = Image.open(file_data)
            
            return image
            
        except UnidentifiedImageError:
            raise ImageValidationError(
                "Cannot identify image file. File may be corrupted or not a valid image."
            )
        except Exception as e:
            raise ImageValidationError(
                f"Error validating image content: {str(e)}"
            )
    
    @staticmethod
    def validate_image_dimensions(image):
        """
        Validates image dimensions to prevent memory exhaustion.
        
        Args:
            image: PIL Image object
            
        Returns:
            tuple: (width, height) if valid
            
        Raises:
            ImageValidationError: If dimensions are invalid
        """
        width, height = image.size
        
        if width < ImageValidator.MIN_DIMENSION or height < ImageValidator.MIN_DIMENSION:
            raise ImageValidationError(
                f"Image dimensions ({width}x{height}) are too small. "
                f"Minimum: {ImageValidator.MIN_DIMENSION}x{ImageValidator.MIN_DIMENSION}"
            )
        
        if width > ImageValidator.MAX_DIMENSION or height > ImageValidator.MAX_DIMENSION:
            raise ImageValidationError(
                f"Image dimensions ({width}x{height}) exceed maximum allowed "
                f"({ImageValidator.MAX_DIMENSION}x{ImageValidator.MAX_DIMENSION}). "
                "This may cause memory issues."
            )
        
        # Check total pixel count to prevent extremely wide/thin images
        total_pixels = width * height
        max_pixels = ImageValidator.MAX_DIMENSION * ImageValidator.MAX_DIMENSION
        
        if total_pixels > max_pixels:
            raise ImageValidationError(
                f"Image contains too many pixels ({total_pixels:,}). "
                f"Maximum allowed: {max_pixels:,}"
            )
        
        return (width, height)
    
    @staticmethod
    def validate_image_mode(image):
        """
        Validates image mode and converts to RGB if needed.
        Some modes may cause issues in processing.
        
        Args:
            image: PIL Image object
            
        Returns:
            PIL.Image.Image: Image in RGB mode
        """
        # Convert to RGB for consistent processing
        # This handles RGBA, P (palette), L (grayscale), etc.
        if image.mode != 'RGB':
            try:
                # Create a white background for transparency
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                else:
                    image = image.convert('RGB')
            except Exception as e:
                raise ImageValidationError(
                    f"Cannot convert image mode '{image.mode}' to RGB: {str(e)}"
                )
        
        return image
    
    @classmethod
    def validate(cls, file_data, filename=None):
        """
        Comprehensive validation of an uploaded image file.
        Performs all security checks in sequence.
        
        Args:
            file_data: File data (bytes, BytesIO, or file-like object)
            filename: Optional filename for extension validation
            
        Returns:
            PIL.Image.Image: Validated and converted RGB image
            
        Raises:
            ImageValidationError: If any validation check fails
        """
        # 1. Validate file extension (if filename provided)
        if filename:
            cls.validate_file_extension(filename)
        
        # 2. Validate file size
        cls.validate_file_size(file_data)
        
        # 3. Validate magic bytes (file signature)
        cls.validate_magic_bytes(file_data)
        
        # 4. Validate image content (PIL can open it)
        image = cls.validate_image_content(file_data)
        
        # 5. Validate dimensions
        cls.validate_image_dimensions(image)
        
        # 6. Validate and convert image mode
        image = cls.validate_image_mode(image)
        
        return image

