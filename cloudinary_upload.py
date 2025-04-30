import os
from dotenv import load_dotenv
import cloudinary
from cloudinary.uploader import upload

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def upload_preserve_folder_structure():
    root_folder = "upload"  # Folder at the same level as the script

    for root, _, files in os.walk(root_folder):
        image_files = [
            f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        ]

        for file in image_files:
            local_path = os.path.join(root, file)

            # Get relative path and convert backslashes to forward slashes
            relative_path = os.path.relpath(local_path, root_folder).replace("\\", "/")
            parent_dir = os.path.dirname(relative_path)
            filename_without_ext = os.path.splitext(os.path.basename(local_path))[0]

            # Use only filename as public_id
            public_id = filename_without_ext

            print(f"Processing: {relative_path}")

            try:
                print(f"Uploading with public_id: '{public_id}', folder: '{parent_dir}'")
                result = upload(
                    local_path,
                    public_id=public_id,
                    resource_type="image",
                    overwrite=True,
                    quality="auto",
                    folder=parent_dir,
                )
                print(f"✅ Uploaded: {local_path} → {result['secure_url']}")
            except Exception as e:
                print(f"❌ Failed to upload {local_path}: {str(e)}")


if __name__ == "__main__":
    upload_preserve_folder_structure()
