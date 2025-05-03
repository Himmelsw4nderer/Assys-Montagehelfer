from flask import Blueprint, render_template, redirect, url_for, request

blueprint = Blueprint('pick_by_light', __name__)

@blueprint.route('/brick_storage', methods=['GET', 'POST'])
def brick_storage():
    if request.method == 'POST':
        # Handle form submission
        pass
    return render_template('brick_storage.html')
