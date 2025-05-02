from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from td.core.utilities import logger
import os, json
import base64
import tempfile


class GoogleDriveLogger:
    def __init__(self, folder_name="trading_log", service_account_file="service_account.json"):
        self.service_account_file = self._get_service_account_file(service_account_file)
        self.folder_name = folder_name
        self.gauth = None
        self.drive = None
        self.folder_id = None
        
        try:
            self._authenticate()
            self.drive = GoogleDrive(self.gauth)
            self.folder_id = self._get_or_create_folder()
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive logger: {e}")
            raise
    def _get_service_account_file(self, service_account_file : str):
        """Handle service account from either env var or file"""
        # Check for encoded JSON in environment variable (GitHub Actions)
        if encoded_json := os.getenv('GOOGLE_SERVICE_ACCOUNT_BASE64'):
            try:
                json_content = base64.b64decode(encoded_json).decode('utf-8')
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
                temp_file.write(json_content)
                temp_file.close()
                return temp_file.name
            except Exception as e:
                logger.error(f"Failed to decode service account: {e}")
                raise

        # Check for direct JSON content (alternative approach)
        if json_content := os.getenv('SERVICE_ACCOUNT_JSON'):
            try:
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
                json.dump(json.loads(json_content), temp_file)
                temp_file.close()
                return temp_file.name
            except Exception as e:
                logger.error(f"Failed to parse JSON service account: {e}")
                raise

        # Fallback to local file (development)
        if os.path.exists(service_account_file):
            return service_account_file
            
        raise FileNotFoundError("No Google Service Account configuration found")
    def _authenticate(self):
        """Authenticate using service account credentials"""
        self.gauth = GoogleAuth()
        scope = ["https://www.googleapis.com/auth/drive"]
        self.gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.service_account_file, 
            scope
        )
    
    def _get_or_create_folder(self):
        """Get or create the log folder in Google Drive"""
        try:
            query = f"title='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            file_list = self.drive.ListFile({'q': query}).GetList()
            
            if file_list:
                return file_list[0]['id']
            else:
                folder = self.drive.CreateFile({
                    'title': self.folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                })
                folder.Upload()
                logger.info(f"Created new folder '{self.folder_name}' in Google Drive with ID: {folder['id']}")
                return folder['id']
        except Exception as e:
            logger.error(f"Failed to get/create folder: {e}")
            raise
    
    def _get_file_id(self, filename):
        """Get file ID if it exists"""
        query = f"title='{filename}' and '{self.folder_id}' in parents and trashed=false"
        file_list = self.drive.ListFile({'q': query}).GetList()
        return file_list[0]['id'] if file_list else None
    
    def write_file(self, filename, content):
        file_id = self._get_file_id(filename)
        
        if file_id:
            # Update existing file
            file = self.drive.CreateFile({'id': file_id})
            file.SetContentString(content)
            file.Upload()
        else:
            # Create new file
            file = self.drive.CreateFile({
                'title': filename,
                'parents': [{'id': self.folder_id}]
            })
            file.SetContentString(content)
            file.Upload()
    
    def read_file(self, filename):
        file_id = self._get_file_id(filename)
        if not file_id:
            return None
            
        file = self.drive.CreateFile({'id': file_id})
        content = file.GetContentString()
        return content
    
    def delete_file(self, filename):
        file_id = self._get_file_id(filename)
        if not file_id:
            return False
            
        file = self.drive.CreateFile({'id': file_id})
        file.Delete()
        return True
    
    def file_exists(self, filename):
        return self._get_file_id(filename) is not None
    