from pydrive.auth import GoogleAuth

gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication

from pydrive.drive import GoogleDrive

drive = GoogleDrive(gauth)

file1 = drive.CreateFile({'title': 'Example.txt'})  # Create GoogleDriveFile instance
file1.SetContentString('This is example document uploaded from my service.') # Set content of the file from given string
file1.Upload()

# Auto-iterate through all files that matches this query
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file_it in file_list:
  print 'title: %s, id: %s' % (file_it['title'], file_it['id'])

downloaded_file = drive.CreateFile({'id': file1['id'], 'mimeType': 'text/plain'})
downloaded_file.GetContentFile('download')
