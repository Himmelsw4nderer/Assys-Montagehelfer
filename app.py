from flask import Flask, render_template, request, redirect, url_for
from blueprint.render import render_blueprint

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('blueprint', step=1))
    return render_template('index.html')

steps = [(1, 1, 2, 1, 'red'), (4, 1, 2, 1, 'blue'), (1, 3, 2, 1, 'green'), (4, 3, 2, 1, 'yellow')]

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
