"""
Supabase Storage Service
Handle file uploads and retrievals from Supabase Storage
"""
from storage3 import create_client as create_storage_client
from fastapi import UploadFile
from typing import Optional
import uuid
import os

from ..core.config import settings
from ..exceptions import BadRequestException


class StorageService:
    def __init__(self):
        # Create storage client directly
        storage_url = f"{settings.SUPABASE_URL}/storage/v1"
        self.client = create_storage_client(
            storage_url,
            {"Authorization": f"Bearer {settings.SUPABASE_KEY}"},
            is_async=False
        )
        self.bucket = settings.SUPABASE_BUCKET
    
    def upload_profile_image(
        self,
        file: UploadFile,
        user_id: int
    ) -> str:
        """
        Upload a profile image to Supabase Storage
        
        Args:
            file: The uploaded file
            user_id: The user's ID
            
        Returns:
            The public URL of the uploaded file
        """
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif"]
        if file.content_type not in allowed_types:
            raise BadRequestException(
                f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Validate file size (max 5MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            raise BadRequestException("File size exceeds 5MB limit")
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"user_{user_id}_{uuid.uuid4()}{file_ext}"
        file_path = f"avatars/{unique_filename}"
        
        try:
            # Upload file to Supabase Storage
            file_content = file.file.read()
            
            # Upload using storage3
            self.client.from_(self.bucket).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": file.content_type}
            )
            
            # Get public URL
            public_url = self.client.from_(self.bucket).get_public_url(file_path)
            
            return public_url
            
        except Exception as e:
            raise BadRequestException(f"Failed to upload file: {str(e)}")
    
    def upload_recipe_image(
        self,
        file: UploadFile,
        recipe_id: int
    ) -> str:
        """
        Upload a recipe image to Supabase Storage
        
        Args:
            file: The uploaded file
            recipe_id: The recipe's ID
            
        Returns:
            The public URL of the uploaded file
        """
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif"]
        if file.content_type not in allowed_types:
            raise BadRequestException(
                f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Validate file size (max 10MB for recipes)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise BadRequestException("File size exceeds 10MB limit")
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"recipe_{recipe_id}_{uuid.uuid4()}{file_ext}"
        file_path = f"recipes/{unique_filename}"
        
        try:
            # Upload file to Supabase Storage
            file_content = file.file.read()
            
            # Upload using storage3
            self.client.from_(self.bucket).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": file.content_type}
            )
            
            # Get public URL
            public_url = self.client.from_(self.bucket).get_public_url(file_path)
            
            return public_url
            
        except Exception as e:
            raise BadRequestException(f"Failed to upload file: {str(e)}")
    
    def upload_cooking_step_media(
        self,
        file: UploadFile,
        recipe_id: int,
        step_number: int
    ) -> str:
        """
        Upload a cooking step media (image/video) to Supabase Storage
        
        Args:
            file: The uploaded file
            recipe_id: The recipe's ID
            step_number: The step number
            
        Returns:
            The public URL of the uploaded file
        """
        # Validate file type (images and videos)
        allowed_types = [
            "image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif",
            "video/mp4", "video/webm", "video/quicktime"
        ]
        if file.content_type not in allowed_types:
            raise BadRequestException(
                f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Validate file size (max 50MB for videos, 10MB for images)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        max_size = 50 * 1024 * 1024 if file.content_type.startswith("video") else 10 * 1024 * 1024
        if file_size > max_size:
            limit = "50MB" if file.content_type.startswith("video") else "10MB"
            raise BadRequestException(f"File size exceeds {limit} limit")
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"recipe_{recipe_id}_step_{step_number}_{uuid.uuid4()}{file_ext}"
        file_path = f"cooking-steps/{unique_filename}"
        
        try:
            # Upload file to Supabase Storage
            file_content = file.file.read()
            
            # Upload using storage3
            self.client.from_(self.bucket).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": file.content_type}
            )
            
            # Get public URL
            public_url = self.client.from_(self.bucket).get_public_url(file_path)
            
            return public_url
            
        except Exception as e:
            raise BadRequestException(f"Failed to upload file: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage
        
        Args:
            file_path: The path of the file to delete (extracted from URL)
            
        Returns:
            True if successful
        """
        try:
            # Extract the path from the full URL if needed
            if file_path.startswith("http"):
                # Extract path after bucket name
                parts = file_path.split(f"/{self.bucket}/")
                if len(parts) > 1:
                    file_path = parts[1]
            
            self.client.from_(self.bucket).remove([file_path])
            return True
            
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Failed to delete file: {str(e)}")
            return False


# Singleton instance
storage_service = StorageService()
