from flask import Flask, render_template
from blueprint.blueprint_router import blueprint as blueprint_blueprint
from pick_by_light.pick_by_light_router import blueprint as pick_by_light_blueprint

app = Flask(__name__)
app.register_blueprint(blueprint_blueprint)
app.register_blueprint(pick_by_light_blueprint)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
