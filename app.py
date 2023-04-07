from flask import Flask, request, jsonify, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps


#Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret key'

#Init db
db = SQLAlchemy(app)

#Init Marshmallow
ma = Marshmallow(app)


#Class/Model
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer)
    
    def __init__(self, content, user_id):
        self.content = content
        self.user_id = user_id
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    
    def __init__(self, name, password):
        self.name = name
        self.password = password
    

#Token required
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


#Schema for blogs
class BlogSchema(ma.Schema):
    class Meta:
        fields = ('id', 'content', 'user_id')
        
blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)


#Schema for users
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'password')

users_schema = UserSchema(many=True)


#Get all users
@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


#Create Blog
@app.route('/blog', methods=['POST'])
@token_required
def add_blog(current_user):
    content = request.json['content']
    user_id = current_user.id
    
    new_blog = Blog(content, user_id)
    
    db.session.add(new_blog)
    db.session.commit()
    
    return blog_schema.jsonify(new_blog)


#Update Blog
@app.route('/blog/<id>', methods=['PUT'])
@token_required
def update_blog(current_user, id):
    blog = Blog.query.get(id)
    
    if blog.user_id != current_user.id:
        return jsonify({'message': 'You cannot update this blog'})
    
    content = request.json['content']
    blog.content = content 
    
    db.session.commit()
    
    return jsonify({'message': 'Updated'})


#Get all blogs
@app.route('/blog', methods=['GET'])
def get_blogs():
    all_blogs = Blog.query.all()
    result = blogs_schema.dump(all_blogs)
    return jsonify(result)


#Get all blogs in pagination
@app.route('/blogpage', methods=['GET'])
def get_blog_page():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    blogs = Blog.query.order_by(Blog.id.desc()).paginate(page=page, per_page=per_page)
    
    result = {
        'items': blogs_schema.dump(blogs.items),
        'total': blogs.total,
        'pages': blogs.pages,
        'page': blogs.page,
        'per_page': blogs.per_page
    }
    return jsonify(result)
    

#Get single blog
@app.route('/blog/<id>', methods=['GET'])
def get_blog(id):
    blog = Blog.query.get(id)
    return blog_schema.jsonify(blog)


#Delete blog
@app.route('/blog/<id>', methods=['DELETE'])
@token_required
def delete_blog(current_user, id):
    blog = Blog.query.get(id)
    
    if blog.user_id != current_user.id:
        return jsonify({'message': 'You cannot delete this blog'})
    
    db.session.delete(blog)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted'})


#User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = User(name=data['name'], password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    response = {'message': f"User {data['name']} has been registered successfully!"}
    return jsonify(response)


#User login - To get token
@app.route('/login')
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    user = User.query.filter_by(name=auth.username).first()
    
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        
        return jsonify({'token': token})
    
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


#Run Server 
if __name__ == '__main__':
    app.run(debug=True)