from flask import Flask, render_template, request, redirect, url_for
from blueprint.render import render_blueprint
from blueprint.loader import select_random_blueprint, load_blueprint

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('blueprint_get', step=1, blueprint=select_random_blueprint()))
    return render_template('index.html')

@app.route('/blueprint', methods=['POST'])
def blueprint_post():
    if 'step' not in request.form or 'blueprint' not in request.form:
        return redirect(url_for('index'))
    step = int(request.form['step'])
    blueprint = request.form['blueprint']

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
        return redirect(url_for('index'))

    img = render_blueprint(steps[:step])
    return render_template('blueprint.html', img=img, step=step, max_steps=max_steps, blueprint=blueprint)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
