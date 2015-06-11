from forms import UserForm, FileForm
from django.http import HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render
from mongoengine.django.auth import User
from django.contrib.auth import logout
import logging
import subprocess
import io
import os
from db_manager import create_document
import xhtml2pdf.pisa as pisa
from mongoengine.django.shortcuts import get_document_or_404
from models import Document

try:
    import StringIO
    StringIO = StringIO.StringIO
except Exception:
    from io import StringIO

logger = logging.getLogger('views')

def createUser(request):
    logger.debug(request.POST)
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.create_user(form.username, form.password)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'registration/createUser.html', {'form': UserForm(), 'error': form.error}) 
    else:
        form = UserForm() 

    return render(request, 'registration/createUser.html', {'form': form}) 

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect("/") 

def saveFile(file_struct):
    file_name = file_struct._name
    with io.open('EditorApp/static/media/' + file_name, 'wb') as file:
        logger.info('Saving file ' + file_name)
        file.write(file_struct.file.getvalue())
    return file_name

def upload(request):
    # Handle file upload
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            logger.debug('File with type ' + request.FILES['docfile'].content_type + ' uploaded.')
            if request.FILES['docfile'].content_type ==  u'application/vnd.oasis.opendocument.text':
                file_name = saveFile(request.FILES['docfile'])
                logger.info('Converting file ' + file_name)
                content = subprocess.check_output(['OdtConverter/odt2html', '-x', 'OdtConverter/odt2html.xsl', 'EditorApp/static/media/' + file_name])
                logger.info('Deleting file ' + file_name)
                os.remove('EditorApp/static/media/' + file_name)
                logger.info('Saving imported document ' + file_name)
                create_document(None, file_name, content)
            elif request.FILES['docfile'].content_type[:5] == u'image':
                saveFile(request.FILES['docfile'])
            else:
                form = FileForm()
                form.error = 'Invalid type of document.'
                logger.error('Wrong type of document.')
                return render(request, 'upload.html', {'form': form})
            # Redirect to the document list after POST
            return HttpResponseRedirect('/')
    else:
        form = FileForm() # A empty, unbound form
    return render(request, 'upload.html', {'form': form})

def get_user_permissions(request):
    user_permissions = []
    if not request.user.is_anonymous():
        for permission in request.user.user_permissions:
            user_permissions.append(permission._DBRef__id)
    return user_permissions

def download(request):
    if request.method == 'GET':
        document = get_document_or_404(Document, id = request.GET.get('documentId'))
        if document.priv == False or document.id in get_user_permissions(request):
            logger.debug('Exporting ' + document.name)
            result = StringIO()
            pdf = pisa.CreatePDF(StringIO(document.text.replace('<img src=\"/static', '<img src=\"EditorApp/static')), result)
            if not pdf.err:
                response = StreamingHttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment;filename=' + document.name.replace(' ', '_') + '.pdf'
                logger.debug('Document ' + document.name + ' was exported successfully')
                return response 
            logger.debug('Failed in export document ' + document.name)
    return HttpResponseRedirect('/')
