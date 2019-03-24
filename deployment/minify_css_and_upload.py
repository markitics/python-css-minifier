CSS_FOLDER = "static/css/"
CSS_FILE_NAME = "customised_css.css"
MIN_FILE_NAME = "customised_css.min.css"
MIN_FILE_WITH_RELATIVE_PATH = "%s%s" % (CSS_FOLDER, MIN_FILE_NAME)
from mymainapp.settings import AWS_PUBLIC_KEY as AWS_ACCESS_KEY
from mymainapp.settings import AWS_SECRET_KEY
from mymainapp.settings import AWS_BUCKET_NAME

def minify_and_upload_customised_css():
    print "Will minify %s, create/overwrite %s" % (CSS_FILE_NAME, MIN_FILE_NAME)
    if minify_customised_css():
        print "Minified to %s, will now upload." % (MIN_FILE_NAME)
        upload_css_to_s3()
        print "All done. Check last updated dates here:"
        print "  https://s3.console.aws.amazon.com/s3/buckets/%s/%s?region=us-east-1&tab=overview" % (AWS_BUCKET_NAME, CSS_FOLDER)
        print "  Sort by 'Last modified'"
    else:
        print "Failed first step; upload aborted."


def minify_customised_css():
    import requests
    url = 'https://cssminifier.com/raw'
    css_file_with_relative_path = "%s%s" % (CSS_FOLDER, CSS_FILE_NAME)
    data = {'input': open(css_file_with_relative_path, 'rb').read()}
    response = requests.post(url, data=data)
    print "Got response, code %s" % (response.status_code)
    if response.status_code == 200:
        minified_css = response.text
        print "Received minified_css from %s" % (url)
        # MIN_FILE_NAME = globally defined above
        f = open(MIN_FILE_WITH_RELATIVE_PATH, "w")
        f.write(minified_css)
        f.close()
        print "Updated %s" % (MIN_FILE_WITH_RELATIVE_PATH)
        return True # True = success
    else:
        print "Error. Operation failed."
        return False # error


def upload_css_to_s3():
    """ Uploade both the .css and .min.css files
        Assumes the .min.css files are already up-to-date

        Aside: If we ran this function from a sub folder, we could do the following to correct the path references
        import sys
        # sys.path.insert(0,'../..') # up two folders
        # in orer to read in the AWS env variables
        sys.path.insert(0,'../') # instead of django.conf settings, import 'mymainapp.settings' directly
        sys.path.insert(0,'../..') allows us to use "python -c 'command'" in bash shell, instead of needing the python manage.py shell
        That is, we don't need Django at all for this simple operation.
        However, simpler to just we assume we run 'gotoapphome' first,
        so this python function is being run from the root my_django_app project folder
        That is:
        In .bashrc, we have alias minifyanduploadcss='gotoapphome; python -c "from deployment.minify_css_and_upload import minify_and_upload_customised_css; minify_and_upload_customised_css();"'
        In my case, 'gotoapphome' is another bashrc alias that activates the virtualenv and jumps to the project's 'root' folder, hence I know the "relative paths" for the .css files will work.
    """
    print "Got bucket (%s), public key (%s) and secret (-%s)" % (AWS_BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY[-5:])
    import boto
    from boto.s3.key import Key
    connection = boto.connect_s3(AWS_ACCESS_KEY, AWS_SECRET_KEY)
    bucket = connection.get_bucket(AWS_BUCKET_NAME, validate=False)
    mykey = Key(bucket)
    for filename in ['customised_css.css', 'customised_css.min.css']:
        local_filename_with_relative_path = "%s%s" % (CSS_FOLDER, filename)
        s3_path_and_filename = CSS_FOLDER + filename # happen to choose same url path on s3 as we do locally
        mykey.key = s3_path_and_filename
        mykey.set_contents_from_filename(local_filename_with_relative_path)
        mykey.set_acl('public-read') # not 'private' or 'authenticated-read'
        print "Success in uploading to s3"
        print "File is at: https://s3.amazonaws.com/%s/%s" % (AWS_BUCKET_NAME, s3_path_and_filename)


