import tensorflow as tf

import shutil
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request,jsonify,json
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import date
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.tools import subprocess_call
from moviepy.config import get_setting
import base64
import re
from io import BytesIO     # for handling byte strings
from io import StringIO
from base64 import b64decode

from pathlib import Path

import moviepy.editor as mpe

from moviepy.editor import *
#from mhmovie.code import *
import glob
import os
import moviepy.video.io.ImageSequenceClip

from GalleryOrganizer import app, db, bcrypt, mail
from GalleryOrganizer.forms import RegistrationForm, LoginForm, UpdateAccountForm, RenameForm, PostForm, RequestResetForm, ResetPasswordForm, SearchForm, ShareForm, SortForm
from GalleryOrganizer.models import User, G_Image
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from GalleryOrganizer.utils import detect_image

from werkzeug.datastructures import FileStorage

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been Created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please Check Email and Password', 'danger')
    return render_template('login.html', title='Login',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been Updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file=image_file, form = form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='mabubakar.cui@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route('/post/<int:post_id>')
def post(post_id):
    image = G_Image.query.get_or_404(post_id)
    return render_template('post.html', title=image.image_actual_name, image=image)

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    image = G_Image.query.get_or_404(post_id)
    db.session.delete(image)
    db.session.commit()
    flash('Your image has been deleted!', 'success')
    return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please Check Email and Password', 'danger')
    return render_template('login.html', title='Login',form=form)

@app.route('/post/<int:post_id>/share', methods=['GET','POST'])
@login_required
def share_post(post_id):
    image = G_Image.query.get_or_404(post_id)
    form = ShareForm()
    if form.validate_on_submit():
        if form.reciever_email.data:
            email_address = form.reciever_email.data
            msg = Message('Shared Image', sender = 'GalleryOrganizer<galleryorganizer@gmail.com>', recipients = [email_address])
            msg.body = 'This Mail is sent by "' + current_user.username + '" from Gallery Organizer'
            f = FileStorage(filename=image.image_name)
            final_image = image.image_name
            image_file = url_for('static', filename='gallery_images/' + image.image_name)
            print(image_file)
            with app.open_resource("static/gallery_images/"+image.image_name) as fp:
                if f.filename.split('.')[1] == 'jpg':
                    msg.attach(image.image_actual_name,"image/jpg",fp.read())
                elif f.filename.split('.')[1] == 'jpeg':
                    msg.attach(image.image_actual_name,"image/jpeg",fp.read())
                elif f.filename.split('.')[1] == 'png':
                    msg.attach(image.image_actual_name,"image/png",fp.read())
            mail.send(msg)
            flash('"'+image.image_actual_name + '" has been shared to: "' + email_address +'"', 'success')
            return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        return render_template('share_image.html', title='Share', form=form, image=image, legend="Share Image")
    return render_template('share_image.html', title='Error', form=form, image=image, legend="Share Image")

def save_g_image(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_an = form_picture.filename
    picture_path = os.path.join(app.root_path, 'static/gallery_images', picture_fn)
    output_size = (525, 525)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    size = os.stat(picture_path).st_size
    return picture_fn, picture_an, picture_path, size

@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.g_image.data:
            picture_fn, picture_an,picture_path,size = save_g_image(form.g_image.data)
            category = detect_image(tf.image.decode_image(open(picture_path, "rb").read(), channels=3))
            print(size)
        image = G_Image(image_name=picture_fn, image_actual_name=picture_an, image_class=category, image_file_size=size, author=current_user)
        db.session.add(image)
        db.session.commit()
        flash('New Image has been Uploaded to "' + category.upper() +"\" Category", 'success')
        return redirect(url_for('home'))
    return render_template('upload_image.html', title='Upload Image', form = form, legend="New Image")

@app.route('/posts/<string:category>', methods=['GET','POST'])
@login_required
def get_posts(category):
    form = SortForm()
    chosen = form.sort_by.data
    # print(chosen)
    if chosen == 1: # Name
        if category == "all":
            images = G_Image.query.filter_by(user_id=current_user.id).order_by(G_Image.image_actual_name).all()
        else:
            images = G_Image.query.filter_by(user_id=current_user.id, image_class=category).order_by(G_Image.image_actual_name).all()
    elif chosen == 2: # DA
        if category == "all":
            images = G_Image.query.filter_by(user_id=current_user.id)
        else:
            images = G_Image.query.filter_by(user_id=current_user.id, image_class=category)
    elif chosen == 3: #DD
        if category == "all":
            images = G_Image.query.filter_by(user_id=current_user.id).order_by(G_Image.date_posted.desc()).all()
        else:
            images = G_Image.query.filter_by(user_id=current_user.id, image_class=category).order_by(G_Image.date_posted.desc()).all()
    elif chosen == 4: #SA
        if category == "all":
            images = G_Image.query.filter_by(user_id=current_user.id).order_by(G_Image.image_file_size).all()
        else:
            images = G_Image.query.filter_by(user_id=current_user.id, image_class=category).order_by(G_Image.image_file_size).all()
    elif chosen == 5: #SD
        if category == "all":
            images = G_Image.query.filter_by(user_id=current_user.id).order_by(G_Image.image_file_size.desc()).all()
        else:
            images = G_Image.query.filter_by(user_id=current_user.id, image_class=category).order_by(G_Image.image_file_size.desc()).all()
    return render_template('posts_all.html', title='Images', images = images, form=form, category=category)


def resizeimages(array):
    path='GalleryOrganizer/static/gallery_images/'
    resized_images = []
    image_list=[]
    for imagename in array:
        img = Image.open(path+imagename)
        image_list.append(img)

    for image in image_list:
        image = image.resize((230, 230))
        resized_images.append(image)
    for (i, new) in enumerate(resized_images):
        new.save('{}{}{}'.format('GalleryOrganizer/static/resize/', i+1, '.jpg'))

def clearresizeimages():
    imagepath = 'GalleryOrganizer/static/resize/'
    outputpath= 'GalleryOrganizer/static/outputvideos/'
    filelist = glob.glob(os.path.join(imagepath, "*.jpg"))
    for f in filelist:
        a=Image.open(f,'r')
        a.close()
        os.remove(f)
    filelist = glob.glob(os.path.join(outputpath, "*.mp4"))
    for f in filelist:
        os.remove(f)

@app.route('/videoclip', methods=['GET','POST'])
@login_required
def videoclip():
    image_folder='GalleryOrganizer/static/resize'
    video_path='GalleryOrganizer/static/videofiles/'
    image_files=[]
    
    if request.method=="POST" and 'array' in request.form:
       
        intro=request.form.get('intro')
        finish=request.form.get('finish')
        print('inn',intro)
        print('lee',len(intro))
        clearresizeimages()
        imagelist=request.form.getlist('array')
        fontsize=request.form.getlist('fontsize')
        textarray=request.form.getlist('textarray')
        colorarray=request.form.getlist('colorarray')
        fontfamily=request.form.getlist('fontfamily')
        fontposition=request.form.getlist('fontposition')
        transition=request.form.getlist('transition1')

      
       # textlist=(request.form.getlist('textarray'))
      
       
       
        string=str(imagelist)
        imagelist=re.sub('[^.,a-zA-Z0-9 \n\.]', '', string)
        string=str(textarray)
        textlist=re.sub('[^.,#a-zA-Z0-9 \n\.]', '', string)
        string=str(colorarray)
        colorarray=re.sub('[^.,#a-zA-Z0-9 \n\.]', '', string)
       
        string=str(fontsize)
        fontsize=re.sub('[^.,#a-zA-Z0-9 \n\.]', '', string)
        string=str(fontfamily)
        fontfamily=re.sub('[^.,#a-zA-Z0-9 \n\.]', '', string)
        string=str(fontposition)
        fontposition=re.sub('[^.,#a-zA-Z0-9 \n\.]', '', string)
        string=str(transition)
        transition=re.sub('[^.,#a-zA-Z0-9 \n\.]', '', string)
        print("string",imagelist)
        imagelist=imagelist.split(',')
        textlist=textlist.split(',')
        colorlist=colorarray.split(',')
        fontsize=fontsize.split(',')
        fontfamily=fontfamily.split(',')
        transition=transition.split(',')
        fontposition=fontposition.split(',')
        
        for k in range(len(fontsize)):
            fontsize[k]=int(fontsize[k])
        
       # textlist=[json.loads(s) for s in textlist]
       
       # print(imagelist)
       
        resizeimages(imagelist)
        fps=int(request.values['fps'])
        trans=str(request.values['transition'])
        for i in range(len(imagelist)-1):
            image_files = [image_folder+'/'+imagelist[i] for imagelist[i] in os.listdir(image_folder) if imagelist[i].endswith(".jpg")]
        
        clips = [ImageClip(a).set_duration(fps) for a in image_files]
        if len(intro)>0:
            txt_clip = TextClip(intro,fontsize=40,color='white').set_duration(fps)
            clips.insert(0,txt_clip)
            textlist.insert(0," ")
            colorlist.insert(0,"white")
            fontsize.insert(0,15)
            fontfamily.insert(0,"Arial")
            fontposition.insert(0,'center')
            transition.insert(0,'crossfadein')
        if len(finish)>0:
            txt_clip = TextClip(finish,fontsize=40,color='white').set_duration(fps)
            clips.append(txt_clip)
            textlist.append(" ")
            colorlist.append("white")
            fontsize.append(15)
            fontfamily.append("Arial")
            fontposition.append('center')
            transition.append('crossfadein')
        print("colorlist",colorlist)
        print("textlist",textlist)
        print("fontsize",fontsize)
        print("fontfamily",fontfamily)
        print("transition",transition)

        


        total_fps=fps*(len(clips)-1)
        if trans=="left":
            slided_clips = [CompositeVideoClip([
                            clip.fx(transfx.slide_in, 1, 'left')]) 
                            for clip in clips]
            final_clip = concatenate( slided_clips, padding=-1)
            final_clip = concatenate_videoclips( slided_clips, method="compose")
            final_clip.write_videofile(video_path+'my_video.mp4', fps=total_fps,codec='png')
        elif trans=="right":
            slided_clips = [CompositeVideoClip([
                            clip.fx( transfx.slide_in, 1, 'right')])
                        for clip in clips]
            final_clip = concatenate( slided_clips, padding=-1)
            final_clip = concatenate_videoclips( slided_clips,  method="compose")
            final_clip.write_videofile(video_path+'my_video.mp4', fps=total_fps, codec='png')
        elif trans=="all":
            transo=['right','top','bottom','left','right','left','bottom','top','right','left','bottom','top']
            slided_clips = [CompositeVideoClip([clip.fx( transfx.slide_in, 1, transo[i])]) for i,clip in enumerate(clips)]
            final_clip = concatenate(slided_clips, padding=-1)
            final_clip = concatenate_videoclips( slided_clips, method="compose")
            final_clip.write_videofile(video_path+'my_video.mp4', fps=total_fps,codec='png')
        elif trans=="slideout":
            slided_clips = [CompositeVideoClip([clip.fx( transfx.slide_out, 1, 'bottom')]) for clip in clips]
            final_clip = concatenate( slided_clips, padding=-1)
            final_clip = concatenate_videoclips( slided_clips, method="compose")
            final_clip.write_videofile(video_path+'my_video.mp4', fps=total_fps,codec='png')
        elif trans=="crossfadein":
            slided_clips = [CompositeVideoClip([clip.fx( transfx.crossfadein, 1)]) for clip in clips]
            final_clip = concatenate( slided_clips, padding=-1)
            final_clip = concatenate_videoclips( slided_clips, method="compose")
            final_clip.write_videofile(video_path+'my_video.mp4', fps=total_fps,codec='png')
        elif trans=="crossfadeout":
            slided_clips = [CompositeVideoClip([clip.fx( transfx.crossfadeout, 1)]) for clip in clips]
            final_clip = concatenate( slided_clips, padding=-1)
            final_clip = concatenate_videoclips( slided_clips, method="compose")
            final_clip.write_videofile(video_path+'my_video.mp4', fps=total_fps,codec='png')
        elif trans=="crossfade":
            slided_clips = [CompositeVideoClip([clip.fx( transfx.crossfadeout, 1).fx(transfx.crossfadein, 1)]) for clip in clips]
            final_clip = concatenate( slided_clips, padding=-1)
            final_clip = concatenate_videoclips( slided_clips, method="compose")
            final_clip.write_videofile(video_path+'my_video.mp4', fps=total_fps,codec='png')
        else:
            final_clip = concatenate_videoclips(clips, method="compose")
       # clip = ImageSequenceClip(image_files, fps=fps)
            final_clip.write_videofile(video_path+'my_video.mp4', fps=total_fps,codec='png')
        
        video=[]
        texts=[]
        clips = [mpe.VideoFileClip(video_path+'my_video.mp4').subclip(i*fps,(fps)*(i+1)) for i in range(len(clips))]
        
       # clips=mpe.VideoFileClip(video_path+'my_video.mp4')
        for i in range(len(textlist)):
            if transition[i]=='None':
                texts.append(TextClip(textlist[i], fontsize=fontsize[i],font=fontfamily[i],  stroke_width=1, color=colorlist[i]).set_position(fontposition[i]).set_duration(fps).set_start(0))
                video.append(CompositeVideoClip([clips[i],texts[i]]))
            if transition[i]=='crossfade':
                texts.append(TextClip(textlist[i], fontsize=fontsize[i],font=fontfamily[i],  stroke_width=1, color=colorlist[i]).set_position(fontposition[i]).set_duration(fps).set_start(0).crossfadein(1).crossfadeout(1))
                video.append(CompositeVideoClip([clips[i],texts[i]]))
            if transition[i]=='crossfadein':
                texts.append(TextClip(textlist[i], fontsize=fontsize[i],font=fontfamily[i],  stroke_width=1, color=colorlist[i]).set_position(fontposition[i]).set_duration(fps).set_start(0).crossfadein(1))
                video.append(CompositeVideoClip([clips[i],texts[i]]))
            if transition[i]=='crossfadeout':
                texts.append(TextClip(textlist[i], fontsize=fontsize[i],font=fontfamily[i],  stroke_width=1, color=colorlist[i]).set_position(fontposition[i]).set_duration(fps).set_start(0).crossfadeout(1))
                video.append(CompositeVideoClip([clips[i],texts[i]]))
           
      #  final_clip = concatenate( video, padding=-1)
        final_clip = concatenate_videoclips( video, method="compose")
        final_clip.write_videofile(video_path+'my_video1.mp4',codec='png')
        # clip = VideoFileClip(video_path+'my_video.mp4').subclip(6, 10)
        # txt_clip = TextClip("My Holidays 2013", fontsize=20, color='white').set_duration(4)
        # video = CompositeVideoClip([clip, txt_clip])
        # video.write_videofile(video_path+'my_video.mp4')
        audio=request.files['audio']
        filename = secure_filename(audio.filename)
        audio_path = os.path.join(app.root_path, 'static/audiofiles', filename)
        audio.save(audio_path)
        my_clip = mpe.VideoFileClip(video_path+'my_video1.mp4')
        audioclip = AudioFileClip(audio_path)
        final = mpe.concatenate_videoclips([my_clip])
        duration=audioclip.set_duration(final.duration)
        final=final.set_audio(duration)
        path_to_download_folder = str(os.path.join(Path.home(), "Downloads"))
        path1 = secrets.token_hex(8)
        final.write_videofile(os.path.join(app.root_path, 'static/outputvideos','outputs.mp4'))
       # final.write_videofile(path_to_download_folder+"\output.mp4")
        final.close()
        final_clip.close()

        return jsonify({"success":"saved"})
        


        
    images = G_Image.query.filter_by(user_id=current_user.id)
    return render_template('videoclip1.html', images = images) 
@app.route('/video', methods=['GET','POST'])
@login_required
def video():
    if request.method=='POST':
        video_path='GalleryOrganizer/static/outputvideos/'
        path_to_download_folder = str(os.path.join(Path.home(), "Downloads"))
        
        if request.args.get('name'):
            my_clip = mpe.VideoFileClip(video_path+'outputs1.mp4')
        else:
            my_clip = mpe.VideoFileClip(video_path+'outputs.mp4')


        my_clip.write_videofile(path_to_download_folder+'\outputs.mp4')
        flash('Video has been Downloaded', 'success')
        return redirect(url_for('home'))
    if request.args.get('name'):
        return render_template('openvideo.html',c=request.args.get('name'))   
    return render_template('openvideo.html')   
@app.route('/trim', methods=['GET','POST'])
@login_required
def trim():
    if request.method=='POST':
        start=int(request.form['start'])
        end=int(request.form['end'])
        
        video_path='GalleryOrganizer/static/outputvideos/'
        my_clip = VideoFileClip(video_path+'outputs.mp4')
       # final=concatenate_videoclips( my_clip, method="compose")
        my_clip=my_clip.subclip(start,end)
        #final=VideoClip( my_clip, method="compose")
        final = concatenate_videoclips([my_clip],method="compose")
      #  ffmpeg_extract_subclip(video_path+'outputs.mp4', start, end, targetname=video_path+'outputs1.mp4')

        final.write_videofile(video_path+'outputs1.mp4')
        return redirect(url_for('video',name="outputs1"))   
        
@app.route('/post/<int:post_id>/edit', methods=['GET','POST'])
@login_required
def edit_post(post_id):
    image = G_Image.query.get_or_404(post_id)
    if request.method=="POST":
        #image_b64 = request.values['imageBase64']
        #image_PIL = Image.open(cStringIO.StringIO(image_b64))
        i = request.values['imageBase64']
        i += "=" * ((4 - len(i) % 4) % 4)
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(image.image_actual_name)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/gallery_images', picture_fn)
        img_bytes = base64.b64decode(i.split(',')[1])
        img = Image.open(BytesIO(img_bytes))
        output_size = (525, 525)
        rgb_im = img.convert('RGB')
        rgb_im.thumbnail(output_size)
        rgb_im.save(picture_path)
        size = os.stat(picture_path).st_size
        category = detect_image(tf.image.decode_image(open(picture_path, "rb").read(), channels=3))
        # print(category)
        image = G_Image(image_name=picture_fn, image_actual_name=image.image_actual_name, 
        image_class=category,image_file_size=size, author=current_user)
        db.session.add(image)
        db.session.commit()
        return jsonify({'success' : 'Image saved successfully!'})
    return render_template('newtemplate.html', title=image.image_actual_name, image=image)

@app.route('/post/<int:post_id>/edit/crop', methods=['GET','POST'])
@login_required
def crop(post_id):
    image = G_Image.query.get_or_404(post_id)
    if request.method=="POST":
        width=request.form['width']
        height=request.form['height']
        x = request.form['x']
        y= request.form['y']
        if  width=="" and height=="" and x=="" and y=="":
            return jsonify({'error' : 'Missing data!'})
        else:
            x=int(x)
            y=int(y)
            width=int(width)+x
            height=int(height)+y
            i=request.values['imagee']
        #i += ("===")
            i += "=" * ((4 - len(i) % 4) % 4)
            img_bytes = base64.b64decode(i.split(',')[1])
            img = Image.open(BytesIO(img_bytes))
        # alpha = rgb_im.split()[-1]
        #rgb_im.putalpha(alpha)
            imagee=img.convert('RGB')
            cropped  = imagee.crop((x,y,width,height))
            cropped.save('GalleryOrganizer/static/cropimages/'+image.image_name)
            return jsonify({'success' : 'Image cropped!'})
    return render_template('newtemplate.html',image=image,imagename=image.image_name)
            
@app.route('/post/<int:post_id>/edit/resize', methods=['GET','POST'])
@login_required
def resize(post_id):
    image = G_Image.query.get_or_404(post_id)
    if request.method=="POST":
        width=request.form['width']
        height=request.form['height']
        if  width=="" and height=="" and x=="" and y=="":
            return jsonify({'error' : 'Missing data!'})
        width=int(width)
        height=int(height)
        i=request.values['imageBase64']
        #i += ("===")
        i += "=" * ((4 - len(i) % 4) % 4)
        img_bytes = base64.b64decode(i.split(',')[1])
        img = Image.open(BytesIO(img_bytes))
        imagergb=img.convert('RGB')
        # alpha = rgb_im.split()[-1]
        # rgb_im.putalpha(alpha)
        newsize=(width,height)
        im1 = imagergb.resize(newsize)
        im1.save('GalleryOrganizer/static/resizeimages/'+image.image_name)
        
    return render_template('newtemplate.html',image=image,resizeimage=image.image_name)

@app.route('/post/<int:post_id>/edit/transform', methods=['GET','POST'])
@login_required
def transform(post_id):
    image = G_Image.query.get_or_404(post_id)
    if request.method=="POST":
        options=str(request.form['option'])
        i=request.values['imageBase64']
        #i += ("===")
        i += "=" * ((4 - len(i) % 4) % 4)
        img_bytes = base64.b64decode(i.split(',')[1])
        img = Image.open(BytesIO(img_bytes))
        imagergb=img.convert('RGB')
        if  options=="fx":
            img = imagergb.transpose(Image.FLIP_LEFT_RIGHT)
        elif options=="fy":
            img = imagergb.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            img = imagergb.transpose(Image.FLIP_TOP_BOTTOM)
        img.save('GalleryOrganizer/static/resizeimages/'+image.image_name)
    return render_template('newtemplate.html',flipimage=image.image_name, image=image)
        
@app.route('/post/<int:post_id>/edit/rotate', methods=['GET','POST'])
@login_required
def rotate(post_id):
    image = G_Image.query.get_or_404(post_id)
    if request.method=="POST":
        i=request.values['imageBase64']
        i += "=" * ((4 - len(i) % 4) % 4)
        img_bytes = base64.b64decode(i.split(',')[1])
        img = Image.open(BytesIO(img_bytes))
        imagergb=img.convert('RGB')
        img= imagergb.rotate(90, resample=Image.BICUBIC,expand=True)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        return img_str
    return render_template('newtemplate.html', image=image ,title=image.image_actual_name)

@app.route('/search', methods=['GET','POST'])
@login_required
def search_post():
    form = SearchForm()
    if form.validate_on_submit:
        if form.image_to_be_searched.data:
            image = G_Image.query.filter_by(user_id=current_user.id, image_actual_name=form.image_to_be_searched.data).first()
            if image:
                flash('Image Found', 'success')
            elif image is None:
                flash('Image Not Found', 'danger')
            return render_template('search_image.html', title='Search', form=form, image=image, legend="Search Image")
    return render_template('search_image.html', title='Search', form=form, legend="Search Image")

@app.route('/post/<int:post_id>/rename', methods=['GET','POST'])
@login_required
def rename_post(post_id):
    image = G_Image.query.get_or_404(post_id)
    form = RenameForm()
    if form.validate_on_submit():
        if form.image_new_name.data:
            image = G_Image.query.filter_by(user_id=current_user.id, id=post_id).first()
            picture_an = form.image_new_name.data
        image.image_actual_name=picture_an
        db.session.commit()
        flash('Image has been Renamed', 'success')
        return redirect(url_for('post', post_id=post_id))
    return render_template('rename_image.html', title='Rename Image', form = form, image=image, legend="Rename Image")