import os
import sys

# Path restructure for imports
script_dir = os.path.dirname( __file__ )
main_dir = os.path.join( script_dir, '..' )
sys.path.append( main_dir )

from web_app.app import create_app

APP = create_app()   # Initializing APP


# Helpful code for development
# set FLASK_ENV=development
# set FLASK_APP=web_app:APP
# import pdb; pdb.set_trace()
# pipenv --rm