from django.shortcuts import render, redirect
from .settings import BASE_DIR
import os
from django.core.files.storage import FileSystemStorage
import shutil
import cv2
from fpdf import FPDF

def upload(request):

    if request.method == "POST":
        show_img = []
        if "session_id" not in request.session.keys():
            request.session["session_id"] = session_id_generator('upload')
            os.mkdir(BASE_DIR/'media/upload'/request.session["session_id"])
            request.session["show_img"] = []
        session_id = request.session["session_id"]
        print("SESSION : ",session_id)
        imgs = request.FILES.getlist('image')
        for img in imgs:
            fs = FileSystemStorage()
            fs.save('upload/'+session_id+'/'+img.name, img)
            show_img.append(img.name)
        request.session["show_img"] += show_img

    return render(request, 'index.html', {
        'images':request.session.get("show_img", []),
        'session_id':request.session.get("session_id", 0),
        })

def session_id_generator(folder):
    sessions = os.listdir(BASE_DIR/'media'/folder)
    i = 0
    while True:
        i += 1
        session_id = str(i)
        if session_id not in sessions:
            break

    if int(session_id) == 10:
        for i in sessions[10::]:
            shutil.rmtree(BASE_DIR/'media'/folder/i)
    elif int(session_id) >= 20:
        for i in sessions[0:10]:
            shutil.rmtree(BASE_DIR/'media'/folder/i)
    return session_id

def process(request, operation):
    content = {}
    session_id = session_id_generator('processed')
    session = request.session["session_id"]
    images = request.session["show_img"]

    os.mkdir(BASE_DIR/'media/processed'/session_id)

    show_img = []
    for image in images:
        img_path = 'media/upload/'+session+'/'+image
        img = cv2.imread(img_path)
        if operation == "to_jpg":
            new_name = image.split('.')[0]+'.jpg'
        elif operation == "to_png":
            new_name = image.split('.')[0]+'.png'
        elif operation == "to_webp":
            new_name = image.split('.')[0]+'.webp'
        elif operation == "to_pdf":
            new_name = image.split('.')[0]+'.jpg'
        else:
            break

        new_path = 'media/processed/'+session_id+'/'+new_name
        cv2.imwrite(new_path, img)
        show_img.append(new_path)
        content["images"] = show_img

        if operation == 'to_pdf':
            content["file"] = create_pdf(show_img, session_id)

    return render(request, 'processed.html', content)

def create_pdf(paths, session_id):
    pdf = FPDF()
    pdf.set_auto_page_break(0)
    for image in paths:
        img = cv2.imread(image)
        s = img.shape
        if s[1]>s[0]:
            pdf.add_page(orientation="landscape")
            pdf.image(image, h=190, w=280)
        else:
            pdf.add_page()
            pdf.image(image, h=270, w=190)
    pdf.output('media/processed/'+session_id+'/Transcript.pdf', 'F')
    return 'media/processed/'+session_id+'/Transcript.pdf'


def clear(request):
    try:
        print("Session Ended: ", request.session["session_id"])
        del request.session["session_id"]
    except:
        print("Session Not Found")
    request.session["show_img"] = []
    return redirect("upload")


