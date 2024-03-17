from flask import Flask, render_template, redirect 
from .models import *

from flask import current_app as app

from flask import session, request, flash, url_for

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    if request.method=='POST':
        new_username = request.form['username']
        user = User.query.filter_by(username=new_username).first()
        if user and user.check_password(request.form['password']):
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    if request.method=='POST':
        new_username = request.form['username']
        user = User.query.filter_by(username=new_username).first() # user or none
        if user:
            flash('Username taken !! Please signup with some other username.')
            return redirect(url_for('signup'))
        
        new_user = User(username=new_username, password='')
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.username
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None) # None here is the value that gets returned when the key 'username' does not exist in the session dictionary
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    blogs = Blog.query.all()
    return render_template('dashboard.html', username = session['username'], blogs=blogs)

from sqlalchemy import or_

# user provides an input and we need to match the records based on the input and show the results to the user
@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    blogs = Blog.query.filter(or_(Blog.title.like(f'%{search_query}%'),Blog.content.like(f'%{search_query}%'))).all()
    return render_template('dashboard.html', username = session['username'], blogs=blogs)

@app.route('/user_search', methods=['POST'])
def user_search():
    search_query = request.form['search_query']
    users = User.query.filter(User.username.like(f'%{search_query}%')).all()
    return render_template('dashboard.html', username = session['username'], users=users)


import os
from werkzeug.utils import secure_filename

@app.route('/create_blog', methods=['GET', 'POST'])
def create_blog():
    user = User.query.filter_by(username=session['username']).first() #to get the current logged in user

    if request.method == 'POST':
        # get the blog details from the form present in the template
        title = request.form['title'] 
        content = request.form['content']
        image = request.files['image']
        if image:
            # to get the filename of the image
            filename = secure_filename(image.filename)
            # to save the image in the folder static/images
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename=None

        # to make a new record of Blog Table
        new_blog = Blog(title=title, content = content, image_url=filename, user_id=user.id)

        db.session.add(new_blog)
        db.session.commit()

        return redirect(url_for('blog', id=new_blog.id))
    
    return render_template('create_blog.html')

@app.route('/blog/<int:id>')
def blog(id):
    blog = Blog.query.get(id)
    current_user = User.query.filter_by(username=session['username']).one()
    print(current_user.has_liked(blog))
    print(current_user)
    print(session['username'])
    return render_template('blog.html', blog=blog, current_user=current_user)

@app.route('/blog/<int:id>/like', methods=['POST'])
def like_blog(id):
    blog = Blog.query.get(id)
    current_user = User.query.filter_by(username=session['username']).one()
    current_user.like(blog)
    return redirect(url_for('blog', id=id))

@app.route('/blog/<int:id>/unlike', methods=['POST'])
def unlike_blog(id):
    blog = Blog.query.get(id)
    current_user = User.query.filter_by(username=session['username']).one()
    current_user.unlike(blog)
    return redirect(url_for('blog', id=id))

@app.route('/blog/delete/<int:id>', methods=['POST'])
def delete_blog(id):
    blog = Blog.query.get(id)
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
def edit_blog(id):
    blog = Blog.query.get(id)
    if request.method=='POST':
        blog.title = request.form['title']
        blog.content = request.form['content']
        db.session.commit()
        return redirect(url_for('blog', id=blog.id))
    return render_template('edit_blog.html', blog=blog)

@app.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    # if user is valid or not

    blogs = Blog.query.filter_by(user_id=user.id).all()
    number_of_blogs = len(blogs)
    

    # if the user page is of the logged in user or not
    if 'username' in session and session['username'] == username:
        # This is the case when The current user is viewing their own profile
        return render_template('user_profile.html', user=user, blogs=blogs, followers=user.followers(), following=user.following(), number_of_blogs=number_of_blogs, is_self=True)
        # is_self is true when The current user is viewing their own profile
    else:
        # i am yash logged in my app and is viewing tejaswin's profile i want to check if yash has followed tejaswin or not 
        # The current user is viewing someone else's profile
        # is_following = False
        current_user = User.query.filter_by(username=session['username']).first()
        is_following=current_user.is_following(user)
        number_followers=len(user.followers())
        number_following= len(user.following())
        print(user.followers())
        print(user.following())
        print(blogs)
        return render_template('user_profile.html', user=user, blogs=blogs, is_self=False, is_following=is_following, followers=user.followers(), following=user.following(), number_of_blogs=number_of_blogs, number_followers=number_followers, number_following=number_following)
        # is_self is False when The current user is viewing someone's else profile
    
@app.route('/follow/<username>')
def follow_route(username):
    user_to_follow = User.query.filter_by(username=username).first() # who we are trying to follow
    current_user = User.query.filter_by(username=session['username']).first() # logged in user
    current_user.follow(user_to_follow)
    return redirect(url_for('user_profile', username=username))

@app.route('/unfollow/<username>')
def unfollow_route(username):
    user_to_unfollow = User.query.filter_by(username=username).first() # who we are trying to follow
    current_user = User.query.filter_by(username=session['username']).first() # logged in user
    current_user.unfollow(user_to_unfollow)
    return redirect(url_for('user_profile', username=username))


# tested with thunder client
@app.route('/user/delete/<username>', methods=['POST'])
def delete_user(username):
    user = User.query.filter_by(username = username).first()
    # something sshould happen here
    Blog.query.filter_by(user_id=user.id).delete()
    Follow.query.filter(or_(Follow.follower_id==user.id, Follow.followed_id==user.id)).delete()
    db.session.delete(user)
    db.session.commit()
    return "deleted"

# in update user that will be same like blog nothing different there just change username/password in the existing record present in the user table
# books in your sections. when you try to delete your section that contains books. then you firts have to delete those books already present in your sections