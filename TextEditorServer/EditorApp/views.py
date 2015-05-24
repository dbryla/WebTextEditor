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

try:
    import StringIO
    StringIO = StringIO.StringIO
except Exception:
    from io import StringIO

logger = logging.getLogger('views')

def createUser(request):
    print request.POST
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
    with io.open('media/' + file_name, 'wb') as file:
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
                content = subprocess.check_output(['OdtConverter/odt2html', '-x', 'OdtConverter/odt2html.xsl', 'media/' + file_name])
                logger.info('Deleting file ' + file_name)
                os.remove('media/' + file_name)
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

def download(request):
    if request.method == 'GET':
        result = StringIO()
        pdf = pisa.CreatePDF(StringIO(request.GET.get('text')), result)
        if not pdf.err:
            response = StreamingHttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment;filename=' + str(request.GET.get('name'))
            return response 
    return HttpResponseRedirect('/')
