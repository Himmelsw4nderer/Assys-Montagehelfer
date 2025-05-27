from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from blueprint.render import render_blueprint, render_control_views
from blueprint.loader import select_random_blueprint, load_blueprint
from pick_by_light.pick_by_light_controller import PickByLightController

# Global state to ensure accessibility across all route functions
state = {
    "auto_acknowledged": False,
    "auto_gesture_ack": True,  # Enable by default for better usability
    "auto_voice_ack": True,    # Enable by default for better usability
    "auto_direction": "next"
}

def create_blueprint(pick_by_light_controller: PickByLightController) -> Blueprint:
    blueprint = Blueprint('blueprint', __name__)

    register_auth_routes(blueprint)
    register_blueprint_routes(blueprint, pick_by_light_controller)
    register_control_routes(blueprint)
    register_auto_acknowledge_routes(blueprint)

    return blueprint

def register_auth_routes(blueprint: Blueprint) -> None:
    @blueprint.route('/log_in', methods=['POST'])
    def log_in():
        return redirect(url_for('blueprint.blueprint_get', step=1, blueprint=select_random_blueprint()))

    @blueprint.route('/log_off', methods=['POST'])
    def log_off():
        return redirect(url_for('index'))

def register_blueprint_routes(blueprint: Blueprint, pick_by_light_controller: PickByLightController) -> None:
    @blueprint.route('/blueprint', methods=['POST'])
    def blueprint_post():
        if 'step' not in request.form or 'blueprint' not in request.form:
            return redirect(url_for('index'))
        step = int(request.form['step'])
        blueprint_name = request.form['blueprint']

        if request.form.get('direction') == 'back':
            return redirect(url_for('blueprint.blueprint_get', step=max(1, step-1), blueprint=blueprint_name))
        return redirect(url_for('blueprint.blueprint_get', step=step+1, blueprint=blueprint_name))

    @blueprint.route('/blueprint', methods=['GET'])
    def blueprint_get():
        if 'blueprint' not in request.args:
            return redirect(url_for('index'))
        blueprint_name = request.args['blueprint']
        if 'step' not in request.args:
            return redirect(url_for('blueprint.blueprint_get', step=1, blueprint=blueprint_name))
        step = int(request.args.get('step', 1))

        steps = load_blueprint(blueprint_name)
        max_steps = len(steps)
        if step > max_steps:
            return redirect(url_for('blueprint.control_get', blueprint=blueprint_name))

        image = render_blueprint(steps[:step])

        location = pick_by_light_controller.get_block_location(length=steps[step-1][2], width=steps[step-1][3], color=steps[step-1][4])

        if location is None:
            warning = "No block found in the storage"
            return render_template('blueprint.html',
                                  image=image,
                                  step=step,
                                  max_steps=max_steps,
                                  blueprint=blueprint_name,
                                  warning=warning)
        else:
            pick_by_light_controller.show_block(location)
            pick_by_light_controller.remove_block(location)

        return render_template('blueprint.html',
                              image=image,
                              step=step,
                              max_steps=max_steps,
                              blueprint=blueprint_name)

def register_control_routes(blueprint: Blueprint) -> None:
    @blueprint.route('/control', methods=['POST'])
    def control_post():
        if 'step' not in request.form or 'blueprint' not in request.form:
            return redirect(url_for('index'))
        blueprint_name = request.form['blueprint']

        if request.form.get('direction') == 'to_last_step':
            steps = load_blueprint(blueprint_name)
            last_step = len(steps)
            return redirect(url_for('blueprint.blueprint_get', step=last_step, blueprint=blueprint_name))
        elif request.form.get('direction') == 'to_first_step':
            return redirect(url_for('blueprint.blueprint_get', step=1, blueprint=blueprint_name))
        return redirect(url_for('blueprint.blueprint_get', step=1, blueprint=select_random_blueprint()))

    @blueprint.route('/control', methods=['GET'])
    def control_get():
        if 'blueprint' not in request.args:
            return redirect(url_for('index'))
        blueprint_name = request.args['blueprint']

        steps = load_blueprint(blueprint_name)
        image_front, image_back, image_right, image_left = render_control_views(steps)
        return render_template('control.html',
                              image_front=image_front,
                              image_right=image_right,
                              image_back=image_back,
                              image_left=image_left,
                              step=len(steps)+1,
                              max_steps=len(steps),
                              blueprint=blueprint_name)

def register_auto_acknowledge_routes(blueprint: Blueprint):
    @blueprint.route("/auto_acknowledge", methods=["GET"])
    def get_auto_acknowledge():
        global state
        print(f"GET auto_acknowledge - current state: {state}")

        if not state.get("auto_acknowledged", False):
            return jsonify({"auto_acknowledged": False, "direction": "next"})

        direction = state.get("auto_direction", "next")

        # Reset state after acknowledgement has been processed
        state["auto_acknowledged"] = False
        state["auto_direction"] = "next"

        print(f"Auto acknowledgment processed with direction: {direction}")

        return jsonify({
            "auto_acknowledged": True,
            "direction": direction
        })

    @blueprint.route("/auto_acknowledge", methods=["POST"])
    def set_auto_acknowledge():
        global state
        print(f"POST auto_acknowledge - current state before: {state}")

        # More robust handling of request data
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            # Try to handle form data as fallback
            data = request.form.to_dict() or {}

        print(f"Received data: {data}")

        ack_type = data.get("type")
        direction = data.get("direction", "next")

        if ack_type == "voice" and state.get("auto_voice_ack", False):
            state["auto_acknowledged"] = True
            state["auto_direction"] = direction
            print(f"Voice acknowledgment received with direction: {direction}")
        elif ack_type == "gesture" and state.get("auto_gesture_ack", False):
            state["auto_acknowledged"] = True
            state["auto_direction"] = direction
            print(f"Gesture acknowledgment received with direction: {direction}")
        elif not ack_type:
            # Direct POST request without type specification
            state["auto_acknowledged"] = True
            state["auto_direction"] = direction
            print(f"Direct acknowledgment received with direction: {direction}")

        print(f"POST auto_acknowledge - current state after: {state}")

        return jsonify({
            "auto_acknowledged": state.get("auto_acknowledged", False),
            "direction": state.get("auto_direction", "next"),
            "ack_type": ack_type,
            "state_debug": state
        })

    @blueprint.route("/settings/update", methods=["POST"])
    def update_settings():
        state["auto_gesture_ack"] = "autoGestureAck" in request.form
        state["auto_voice_ack"] = "autoVoiceAck" in request.form
        return redirect(url_for("index"))

    @blueprint.route("/settings/current", methods=["GET"])
    def get_current_settings():
        return jsonify({
            "auto_gesture_ack": state["auto_gesture_ack"],
            "auto_voice_ack": state["auto_voice_ack"],
        })
