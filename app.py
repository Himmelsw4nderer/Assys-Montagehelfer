from flask import Flask, render_template
from blueprint.blueprint_router import create_blueprint as create_blueprint_blueprint
from pick_by_light.pick_by_light_router import create_blueprint as create_pick_by_light_blueprint
from pick_by_light.pick_by_light_controller import PickByLightController

pick_by_light_controller = PickByLightController()
blueprint_blueprint = create_blueprint_blueprint(pick_by_light_controller)
pick_by_light_blueprint = create_pick_by_light_blueprint(pick_by_light_controller)

app = Flask(__name__)
app.register_blueprint(blueprint_blueprint)
app.register_blueprint(pick_by_light_blueprint)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
