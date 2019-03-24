
# Context

* Any app (in this case, a Django app, but need not be Django, or even Python)
* Want static files in the code base so we can track changes.
* Want to only ever manipulate the .css (not minified).
* Want to serve a minified .min.css file from s3 (not from app).
```html
    <-- This cdn.example.com CNAME points to CloudFront, which in turn pulls from AWS S3 bucket called 'mybucket' -->
    <link href="https://cdn.example.com/static/css/customised_css.min.css" rel="stylesheet">
```
In local development, you can choose to read the local `customised_css.css` directly.

I use python to minify the .css and upload to S3.

# Method
* Use Python requests to make a POST request to [`cssminifier.com`](https://cssminifier.com)'s API endpoint.
* Use Python ([`boto`](https://boto.readthedocs.io/en/latest://boto.readthedocs.io/en/latest/))to upload the resopnse as a .min.css file to AWS S3.

# In this code repo
This is a **fragment** of a Django app.  
It doesn't work as-is, but has a few files so you can see how I've chosen to arrange them.
Key "minify and upload css" code is in 
[`deployment/`](deployment/minify_css_and_upload.py) folder.


# Setup

'home' / 'root' folder is `my_django_app`.
`my_django_app` folder sits in a virtual env called `virtualenvfolder`, alongside the virtual env folders like `bin/`, `etc/`, `include/`, `lib/`, `share/`

`my_django_app` project folder has:
* a bunch of app folders, such as `mymainapp/`
* a specific `deployment` folder which contains file [`minify_css_and_upload.py`](deployment/minify_css_and_upload.py)
* static files (.js and .css etc.) in `static/` folder

On my computer, I have the following lines
```
# extracts from .bashrc
alias uprofile='. ~/.bashrc' # ('updated profile' = reload this file)
alias gotoapphome='uprofile; cd ~/path/to/virtualenvfolder/; . bin/activate; cd my_django_app'
# activating virtual env is irrelevant for this example; what's key is cd my_django_app
alias minifyanduploadcss='gotoapphome; python -c "from deployment.minify_css_and_upload import minify_and_upload_customised_css; minify_and_upload_customised_css();"'
```


# Result
Two-step process:
* Edit `customised_css.css` to make whatever changes you like. You can easily have the html read the local version using staticfiles, instead of reading from s3, during development.
* Once you're happy with your new .css file: In normal bash shell, run the one-word command `minifyanduploadcss`, and that will create `customised_css.min.css` and upload it to your s3 bucket. (I use CloudFront as CDN.)

```
# normal bash shell (anywhere on your computer)
~$ minifyanduploadcss
Will minify customised_css.css, create/overwrite customised_css.min.css
Got response, code 200
Received minified_css from https://cssminifier.com/raw
Updated static/css/customised_css.min.css
Minified to customised_css.min.css, will now upload.
Got bucket (mybucket), public key (AKIA0123456789) and secret (-ua5cu)
Success in uploading to s3
File is at: https://s3.amazonaws.com/mybucket/static/css/customised_css.css
Success in uploading to s3
File is at: https://s3.amazonaws.com/mybucket/static/css/customised_css.min.css
All done. Check last updated dates here:
  https://s3.console.aws.amazon.com/s3/buckets/mybucket/static/css/?region=us-east-1&tab=overview
  Sort by 'Last modified'
~$
```

Note: You may need to clear your browser cache to see changes on CloudFront/S3 files. 
