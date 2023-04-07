This is a blog app api where users can post their blogs.

At first you must activate the virtual environment. Here it is the 'env' folder.
To activate it type in terminal - source env/scripts/activate

If you want to create your own virtual env - install all the requirements through 'requirements.txt' file.
To install requirements in your vir env - pip install requirements.txt

After activating the vir env satrt program by
typing 'python app.py' in your terminal

Use Postman to test the API

http://127.0.0.1:5000/register - Here we can register new users.

http://127.0.0.1:5000/login - Once the user is registered go to authorization and select basic auth. Enter the username and password of registered users. You will get a token.

#Token
In postman go to the Headers part. In KEY put x-access-token and in VALUE copy and paste the token acquired from above. Do the same for all paths that require authentication.

http://127.0.0.1:5000/blog
    Read - Here you can get all the lists of the blogs using the GET method.
        
           By passing the id of the blog at last for example:/blog/1 you can view the single blog.

    Create - You can also create your own blog using the POST method. To use POST method you must have token. While creating the blog only write the content part.

    Update - By PUT method you can update the blog. 

    Delete - By DELETE method you can delete the blog.

    Both PUT and DELETE method require token.

    The blog can be updated and deleted by it's owner only while it can be viewed by others too. 

http://127.0.0.1:5000/blogpage - This is the path to view the blogs with pagination.






