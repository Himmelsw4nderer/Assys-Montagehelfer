from flask import Flask, render_template, request, redirect, url_for
from blueprint.render import render_blueprint, render_control_views
from blueprint.loader import select_random_blueprint, load_blueprint

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/log_in', methods=['POST'])
def log_in():
    return redirect(url_for('blueprint_get', step=1, blueprint=select_random_blueprint()))

@app.route('/log_off', methods=['POST'])
def log_off():
    return redirect(url_for('index'))

@app.route('/blueprint', methods=['POST'])
def blueprint_post():
    if 'step' not in request.form or 'blueprint' not in request.form:
        return redirect(url_for('index'))
    step = int(request.form['step'])
    blueprint = request.form['blueprint']

    if request.form.get('direction') == 'back':
        return redirect(url_for('blueprint_get', step=max(1, step-1), blueprint=blueprint))
    return redirect(url_for('blueprint_get', step=step+1, blueprint=blueprint))

@app.route('/blueprint', methods=['GET'])
def blueprint_get():
    if 'blueprint' not in request.args:
        return redirect(url_for('index'))
    blueprint = request.args['blueprint']
    if 'step' not in request.args:
        return redirect(url_for('blueprint_get', step=1, blueprint=blueprint))
    step = int(request.args.get('step', 1))

    steps = load_blueprint(blueprint)
    max_steps = len(steps)
    if step > max_steps:
        return redirect(url_for('control_get', blueprint=blueprint))

    image = render_blueprint(steps[:step])
    return render_template('blueprint.html', image=image, step=step, max_steps=max_steps, blueprint=blueprint)

@app.route('/control', methods=['POST'])
def control_post():
    if 'step' not in request.form or 'blueprint' not in request.form:
        return redirect(url_for('index'))
    step = int(request.form['step'])
    blueprint = request.form['blueprint']

    if request.form.get('direction') == 'back':
        return redirect(url_for('blueprint_get', step=max(1, step-1), blueprint=blueprint))
    return redirect(url_for('blueprint_get', step=1, blueprint=select_random_blueprint()))

@app.route('/control', methods=['GET'])
def control_get():
    if 'blueprint' not in request.args:
        return redirect(url_for('index'))
    blueprint = request.args['blueprint']

    steps = load_blueprint(blueprint)
    image_front, image_back, image_right, image_left = render_control_views(steps)
    return render_template('control.html', image_front=image_front, image_right=image_right, image_back=image_back, image_left=image_left , step=len(steps)+1, max_steps=len(steps), blueprint=blueprint)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
