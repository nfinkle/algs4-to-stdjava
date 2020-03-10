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
    return render_template('home.html')


@app.route('/index.html')
# @app.route()
def show_index():
    return render_template('index.html', is_about=False)


@app.route('/about_auth.html')
def show_about_auth():
    return render_template('about_auth.html', is_about=True)


@app.route('/about_unauth.html')
def show_about_unauth():
    return render_template('about_unauth.html')


# @app.errorhandler(400)
# def handle_bad_request(e):
#     print(e.description)
#     return render_template('400_error.html', e=e.description), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    show_index()
