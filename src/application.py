import os, shutil
from datetime import datetime
from flask import flash, Flask, render_template, request
from dlp_ingest.lambda_function import main as dlp_ingest_main


application = Flask(__name__)
application.config['APPLICATION_ROOT'] = os.path.dirname(os.path.abspath(__file__))
application.config['DEBUG'] = True
application.config['SECRET_KEY'] = os.urandom(24)
application.config['UPLOAD_FOLDER'] = os.path.join(application.config['APPLICATION_ROOT'], 'uploads')
application.config['ALLOWED_EXTENSIONS'] = {'csv'}

def cleanup(directory):
    try:
        shutil.rmtree(directory, ignore_errors=True)
        os.makedirs(directory)
    except:
        pass

cleanup(application.config['UPLOAD_FOLDER'])


# TODO: split route handlers into separate classes
    

def get_identifier():
    return request.form.get('collection_identifier')


def get_files():
    files = []
    try:
        files = [f for f in os.listdir(application.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(application.config['UPLOAD_FOLDER'], f))]
    except Exception as e:
        pass
    return files


def files_exist():
    return len(get_files()) > 0



def get_input_filename(identifier, file, i, num_files):
    indexPrefix = ""
    for j in range(len(str(num_files)) - len(str(i))):
        indexPrefix += "0"
    index = f"{indexPrefix}{i}"
    return f"{identifier}_{index}.{file.filename.split('.')[-1]}"


def save_uploads(identifier, num_files):
    try:
        i = 0
        for file in request.files.getlist('metadata-input'):
            if file and file.filename.endswith(tuple(application.config['ALLOWED_EXTENSIONS'])):
                file.save(os.path.join(application.config['UPLOAD_FOLDER'], f"{get_input_filename(identifier, file, i, num_files)}"))
                i += 1
    except Exception as e:
        print(e)




@application.route('/submit', methods=['GET', 'POST'])
def submit():
    timestamp = str(datetime.today()).replace(" ", "_")
    identifier = get_identifier()
    if request.method == 'POST' and 'metadata-input' in request.files:
        save_uploads(identifier, len(request.files.getlist('metadata-input')))

    if files_exist():
        flash('Metadata uploaded successfully. Ingesting...')
        # Do the ingest
        
    return render_template('submit.html')


@application.route('/')
def index():
    return render_template('index.html')




if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8000)