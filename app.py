from flask import Flask, request, render_template, url_for
import flask_bootstrap
# from flask_cors import CORS

app = Flask(__name__)
flask_bootstrap.Bootstrap(app)
# CORS(app)
# app.register_blueprint(import_backup_api)


@app.route('/health', methods=['GET'])
def health():
    return "I\'m online"


# @app.route('/api.html')
# @app.route('/api')
# def show_api():
#     return render_template('api.html')

@app.route('/')
@app.route('/home')
@app.route('/home.html')
def show_home():
    return render_template('home.html', is_about=False)


@app.route('/index.html')
# @app.route()
def show_index():
    progress = {'print': 50, 'scanner': 20, 'else': 15}
    progressBars = {}
    for key, val in progress.items():
        progressBars[key] = "<div class='progress-bar' role='progressbar' style='width: " + \
            str(val) + "%' aria-valuenow='" + str(val) + \
            "%' aria-valuemin='0' aria-valuemax='100'> </div>"
    return render_template('index.html', is_about=False, progressBars=progressBars)


@app.route('/module.html')
def show_module():
    return render_template('module.html', is_about=False)


@app.route('/system-out.html')
def show_system_out():
    return render_template('system-out.html', is_about=False)


@app.route('/about_auth.html')
def show_about_auth():
    return render_template('about_auth.html', is_about=True)


@app.route('/about_unauth.html')
def show_about_unauth():
    return render_template('about_unauth.html', is_about=True)


@app.errorhandler(404)
def handle_bad_request(e):
    print(e.description)
    return render_template('404_error.html', e=e.description), 404


if __name__ == "__main__":
    app.run(debug=True, development=True)
    show_index()
