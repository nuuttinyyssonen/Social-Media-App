from flask import render_template, Blueprint
import random
from ...Models.queries import *
import base64

explore_bp = Blueprint('explore_bp', __name__)

# Explore route for scrolling through all images
@explore_bp.route('/explore', methods=['GET', 'POST'])
def explore():
    random_images = ImgQueries.get_all()
    random.shuffle(random_images)
    return render_template('./main/explore.html', random_images=random_images)

# This function to query images from db and it's used all over in the code
def b64encode(data):
    return base64.b64encode(data).decode("UTF-8")