from flask import Flask, render_template, request, redirect, url_for, jsonify
from blueprint.render import render_blueprint, render_control_views
from blueprint.loader import select_random_blueprint, load_blueprint
from pick_by_light.pick_by_light_controller import PickByLightController
from queue import Queue

message_queue = Queue()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/log_in', methods=['POST'])
def log_in():
    return redirect(url_for('blueprint_get', step=1, blueprint=select_random_blueprint()))

@app.route('/auto_acknowledge', methods=['POST'])
def auto_acknowledge():
    """Endpoint for automatic acknowledgment from camera/speech/keyword recognition."""
    # Check if we're in blueprint or control view
    if request.referrer and 'blueprint' in request.referrer:
        # Extract current step and blueprint from referrer URL
        parts = request.referrer.split('?', 1)
        if len(parts) > 1:
            query_params = dict(param.split('=') for param in parts[1].split('&'))
            if 'step' in query_params and 'blueprint' in query_params:
                step = int(query_params['step'])
                blueprint = query_params['blueprint']
                # Move to next step
                return redirect(url_for('blueprint_get', step=step+1, blueprint=blueprint))
    
    # If unable to determine context or in control view, just return success
    return jsonify({"success": True, "message": "Acknowledgment received"})

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
    artnet_controller = PickByLightController(message_queue)
    artnet_controller.daemon = True
    artnet_controller.start()

    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        artnet_controller.stop()
        artnet_controller.join()
