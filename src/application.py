import os, shutil, sys, yaml
from datetime import datetime
from flask import flash, Flask, render_template, request
from dlp_ingest.lambda_function import main as dlp_ingest_main


application = Flask(__name__)
application.config['APPLICATION_ROOT'] = os.path.dirname(os.path.abspath(__file__))
application.config['STATIC'] = os.path.join(application.config['APPLICATION_ROOT'], 'static')
application.config['DEBUG'] = True
application.config['SECRET_KEY'] = os.urandom(24)
application.config['UPLOADS'] = os.path.join(application.config['APPLICATION_ROOT'], 'uploads')
application.config['ALLOWED_EXTENSIONS'] = {'csv'}

env_vars = [
    'VERBOSE',
    'AWS_SRC_BUCKET',
    'AWS_DEST_BUCKET',
    'COLLECTION_CATEGORY',
    'COLLECTION_IDENTIFIER',
    'COLLECTION_SUBDIRECTORY',
    'ITEM_SUBDIRECTORY',
    'REGION',
    'DYNAMODB_TABLE_SUFFIX',
    'DYNAMODB_NOID_TABLE',
    'DYNAMODB_FILE_CHAR_TABLE',
    'APP_IMG_ROOT_PATH',
    'NOID_SCHEME',
    'NOID_NAA',
    'LONG_URL_PATH',
    'SHORT_URL_PATH',
    'MEDIA_INGEST',
    'MEDIA_TYPE',
    'METADATA_INGEST',
    'GENERATE_THUMBNAILS',
    'DRY_RUN',
    'UPDATE_METADATA'
]

def cleanup(directory):
    try:
        shutil.rmtree(directory, ignore_errors=True)
        os.makedirs(directory)
    except:
        pass

cleanup(application.config['UPLOADS'])
    

def get_identifier():
    return request.form.get('collection_identifier')


def get_files():
    files = []
    try:
        files = [f for f in os.listdir(application.config['UPLOADS']) if os.path.isfile(os.path.join(application.config['UPLOADS'], f))]
    except Exception as e:
        pass
    return files


def files_exist():
    return len(get_files()) > 0



def get_input_filename(identifier, file, i, num_files):
    # indexPrefix = ""
    # for j in range(len(str(num_files)) - len(str(i))):
    #     indexPrefix += "0"
    # index = f"{indexPrefix}{i}"
    return str(file.filename)
    # return f"{identifier}_{index}_{file.filename}"


def save_uploads(identifier, num_files):
    files = []
    try:
        i = 0
        for file in request.files.getlist('metadata_input'):
            if file and file.filename.endswith(tuple(application.config['ALLOWED_EXTENSIONS'])):
                input_filename = get_input_filename(identifier, file, i, num_files)
                files.append(input_filename)
                file.save(os.path.join(application.config['UPLOADS'], f"{input_filename}"))
                i += 1
    except Exception as e:
        print(e)

    return files

def set_environment(env_values):
    for key, value in env_values:
        if str(key).upper() in env_vars:
            application.config[str(key).upper()] = value


def set_environment_defaults():
    defaults = None
    env_file = os.path.join(application.config['APPLICATION_ROOT'], 'static', 'yml', os.getenv('INGEST_ENV_YAML'))
    with open(env_file, 'r') as f:
        defaults = yaml.safe_load(f)
    if defaults:
        set_environment(defaults.items())
    else:
        print(f"Error loading environment defaults from {env_file}")
        sys.exit(1)


def set_environment_overrides():
    set_environment(request.form.items())


@application.route('/submit', methods=['GET', 'POST'])
def submit():
    uploaded = []
    timestamp = str(datetime.today()).replace(" ", "_")

    # set_environment_defaults()
    collection_identifier = get_identifier()
    if request.method == 'POST' and 'metadata_input' in request.files:
        uploaded = save_uploads(collection_identifier, len(request.files.getlist('metadata_input')))

    if files_exist():
        set_environment_overrides()

        # Do the ingest
        metadata_filepath = os.path.join(application.config['UPLOADS'], uploaded[0])
        dlp_ingest_main(None, None, metadata_filepath, application.config)
        flash(f"Ingested:")
        flash(uploaded[0])
        flash(f"into collection: {collection_identifier}")
        
    return render_template('submit.html')


@application.route('/')
def index():
    return render_template('index.html')




if __name__ == "__main__":
    set_environment_defaults()

    application.run(host='0.0.0.0', port=8000)