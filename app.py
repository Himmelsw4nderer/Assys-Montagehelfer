from flask import Flask, render_template, request, redirect, url_for
from blueprint.render import render_blueprint

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('blueprint', step=1))
    return render_template('index.html')

steps = [(1, 1, 4, 2, 'red'), (5, 1, 2, 4, 'blue'), (1, 3, 4, 2, 'green'), (3, 2, 4, 2, 'yellow')]

@app.route('/blueprint', methods=['GET', 'POST'])
def blueprint():
    if request.method == 'POST':
        step = int(request.form['step']) + 1
        return redirect(url_for('blueprint', step=step))
    step = request.args.get('step', 1)
    img = render_blueprint(steps[:int(step)])
    return render_template('blueprint.html', img=img, step=step)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
