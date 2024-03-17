# http request methods -> get, post 
# http methods -> put -> create something new
# http methods -> delete -> to delete something

from flask_restful import Resource
from flask import request
from .models import *

class HelloWorld(Resource):
    def get(self):
        return {'Hello' : 'world'} # a python dictionary has a key: value pair
    
class BlogAPI(Resource):
    def get(self, id): # Read in CRUD
        blog = Blog.query.get(id)
        if blog is None:
            return {'error':'Blog not found'}, 404 
        return {
            'id': blog.id,
            'title': blog.title,
            'content': blog.content
        }, 200
    
    def post(self):
        # course -> reqparse
        # creating a new blog
        args = request.get_json()
        new_blog = Blog(user_id = args['user_id'], title=args['title'], content=args['content'])
        db.session.add(new_blog)
        db.session.commit()
        return {'message': 'Blog created!!', 'blog details': {'id': new_blog.id,
            'title': new_blog.title,
            'content': new_blog.content}}, 201
    
    def put(self, id):
        # updating an existing blog
        blog = Blog.query.get(id)
        data = request.get_json()
        if blog is None:
            return {'error':'Blog not found'}, 404
        blog.title = data['title']
        blog.content = data['content']
        db.session.commit()
        return {'message': 'Blog Updated!!', 'blog details': {'id': blog.id,
            'title': blog.title,
            'content': blog.content}}, 200
    
    # delete is left
    def delete(self, id):
        blog = Blog.query.get(id)
        if blog is None:
            return {'error':'Blog does not exist'}, 404
        db.session.delete(blog)
        db.session.commit()
        return {'message':'Blog Deleted :('}, 200
    
# APIs for CRUD on User 