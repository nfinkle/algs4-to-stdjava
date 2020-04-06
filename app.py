import jpype.imports
from py4j.java_gateway import JavaGateway
from flask import Flask, request, render_template, url_for
# import flask_bootstrap
# from flask_cors import CORS
import os

app = Flask(__name__)
# flask_bootstrap.Bootstrap(app)
# CORS(app)
# app.register_blueprint(import_backup_api)


@app.route('/health', methods=['GET'])
def health():
    os.system('javac tester.java')
    os.system('java tester > answer.txt')
    with open("answer.txt") as fd:
        return fd.read()
    return "I'm online"


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
def show_index():
    progress = {'print': 50, 'scanner': 20, 'else': 15}
    progressBars = {}
    for key, val in progress.items():
        progressBars[key] = "<div class='progress-bar' role='progressbar' style='width: " + \
            str(val) + "%' aria-valuenow='" + str(val) + \
            "%' aria-valuemin='0' aria-valuemax='100'> </div>"
    return render_template('index.html', is_about=False, progressBars=progressBars)


@app.route('/modules/module.html')
def show_module():
    return render_template('modules/module.html', is_about=False, constructors=True)


@app.route('/modules/system-out.html')
def show_system_out():
    return render_template('modules/system-out.html', is_about=False, constructors=False)


@app.route('/modules/scanner.html')
def show_scanner():
    return render_template('modules/scanner.html', is_about=False, constructors=True)


@app.route('/modules/printwriter.html')
def show_printwriter():
    return render_template('modules/printwriter.html', is_about=False, constructors=True)


@app.route('/modules/hashmap.html')
def show_hashmap():
    return render_template('modules/hashmap.html', is_about=False, constructors=True)


@app.route('/modules/hashset.html')
def show_hashset():
    return render_template('modules/hashset.html', is_about=False, constructors=True)


@app.route('/modules/treemap.html')
def show_treemap():
    return render_template('modules/treemap.html', is_about=False, constructors=True)


@app.route('/modules/priorityqueue.html')
def show_priorityqueue():
    return render_template('modules/priorityqueue.html', is_about=False, constructors=True)


@app.route('/modules/queue.html')
def show_queue():
    return render_template('modules/queue.html', is_about=False, constructors=True)


@app.route('/modules/stack.html')
def show_stack():
    return render_template('modules/stack.html', is_about=False, constructors=True)


"""
@app.route('/run_code')
def run_code():

    # def run_code(the_code):
    # from java.lang import System
    # // Prepare source somehow.
    source = "package test; public class Test { static { System.out.println(\"hello\"); } public Test() { System.out.println(\"world\"); } }"
    import jpype
    import jpype.imports
    jpype.startJVM()
    from java.io import File
    # // Save source in .java file.
    File root = new File("/java")
    # // On Windows running on C: \, this is C: \java.
    File sourceFile = new File(root, "test/Test.java")
    sourceFile.getParentFile().mkdirs()
    Files.write(sourceFile.toPath(), source.getBytes(StandardCharsets.UTF_8))
    # // Compile source file.
    JavaCompiler compiler = ToolProvider.getSystemJavaCompiler()
    compiler.run(null, null, null, sourceFile.getPath())
    # // Load and instantiate compiled class.
    URLClassLoader classLoader = URLClassLoader.newInstance(new URL[] {root.toURI().toURL()})
    Class <?> cls = Class.forName("test.Test", true, classLoader)
    # // Should print "hello".
    Object instance = cls.newInstance()
    # // Should print "world".
    System.out.println(instance)
    # // Should print "test.Test@hashcode".
"""


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
