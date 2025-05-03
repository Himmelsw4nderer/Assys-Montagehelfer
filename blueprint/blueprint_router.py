from flask import Blueprint, render_template, redirect, url_for, request
from blueprint.render import render_blueprint, render_control_views
from blueprint.loader import select_random_blueprint, load_blueprint

blueprint = Blueprint('blueprint', __name__)

@blueprint.route('/log_in', methods=['POST'])
def log_in():
    return redirect(url_for('blueprint.blueprint_get', step=1, blueprint=select_random_blueprint()))

@blueprint.route('/log_off', methods=['POST'])
def log_off():
    return redirect(url_for('index'))

@blueprint.route('/blueprint', methods=['POST'])
def blueprint_post():
    if 'step' not in request.form or 'blueprint' not in request.form:
        return redirect(url_for('index'))
    step = int(request.form['step'])
    blueprint = request.form['blueprint']

    if request.form.get('direction') == 'back':
        return redirect(url_for('blueprint.blueprint_get', step=max(1, step-1), blueprint=blueprint))
    return redirect(url_for('blueprint.blueprint_get', step=step+1, blueprint=blueprint))

@blueprint.route('/blueprint', methods=['GET'])
def blueprint_get():
    if 'blueprint' not in request.args:
        return redirect(url_for('index'))
    blueprint = request.args['blueprint']
    if 'step' not in request.args:
        return redirect(url_for('blueprint.blueprint_get', step=1, blueprint=blueprint))
    step = int(request.args.get('step', 1))

    steps = load_blueprint(blueprint)
    max_steps = len(steps)
    if step > max_steps:
        return redirect(url_for('blueprint.control_get', blueprint=blueprint))

    image = render_blueprint(steps[:step])
    return render_template('blueprint.html', image=image, step=step, max_steps=max_steps, blueprint=blueprint)

@blueprint.route('/control', methods=['POST'])
def control_post():
    if 'step' not in request.form or 'blueprint' not in request.form:
        return redirect(url_for('index'))
    step = int(request.form['step'])
    blueprint = request.form['blueprint']

    if request.form.get('direction') == 'back':
        return redirect(url_for('blueprint.blueprint_get', step=max(1, step-1), blueprint=blueprint))
    return redirect(url_for('blueprint.blueprint_get', step=1, blueprint=select_random_blueprint()))

@blueprint.route('/control', methods=['GET'])
def control_get():
    if 'blueprint' not in request.args:
        return redirect(url_for('index'))
    blueprint = request.args['blueprint']

    steps = load_blueprint(blueprint)
    image_front, image_back, image_right, image_left = render_control_views(steps)
    return render_template('control.html', image_front=image_front, image_right=image_right, image_back=image_back, image_left=image_left , step=len(steps)+1, max_steps=len(steps), blueprint=blueprint)
