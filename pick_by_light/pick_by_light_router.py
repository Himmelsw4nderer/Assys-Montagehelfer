from flask import Blueprint, render_template, redirect, url_for, request
from pick_by_light.pick_by_light_controller import PickByLightController

def create_blueprint(pick_by_light_controller: PickByLightController) -> Blueprint:
    blueprint = Blueprint('pick_by_light', __name__)

    @blueprint.route('/brick_storage', methods=['GET', 'POST'])
    def brick_storage():
        if request.method == 'POST':
            color = request.form.get('color')
            length = request.form.get('length')
            width = request.form.get('width')
            location = request.form.get('location')
            count = request.form.get('count')

            if color and length and width and location:
                try:
                    length = int(length)
                    width = int(width)
                    location = int(location)
                    count = int(count) if count is not None else 0

                    pick_by_light_controller.add_block_to_location(location, width, length, color, count)
                    return redirect(url_for('pick_by_light.brick_storage'))
                except ValueError:
                    return render_template('brick_storage.html', blocks=pick_by_light_controller.blocks)
            pass
        return render_template('brick_storage.html', blocks=pick_by_light_controller.blocks)
    return blueprint
