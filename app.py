from flask import Flask, request, render_template, url_for, jsonify
# import flask_bootstrap
import worker
import rq
# from flask_cors import CORS
import os

app = Flask(__name__)
# flask_bootstrap.Bootstrap(app)
# CORS(app)
# app.register_blueprint(import_backup_api)


@app.route('/health', methods=['GET'])
def health():
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


@app.route('/about_auth.html')
def show_about_auth():
    return render_template('about_auth.html', is_about=True)


q = rq.Queue(connection=worker.conn)
@app.route('/run_code_with_code')
def run_code_get_code():
    text = request.args["code"]
    return run_code(text=text)


@app.route('/run_code')
def run_code(text=None):
    if text is None:
        text = 'import edu.princeton.cs.algs4.StdOut; public class new_test { public static void main(String[] args) { StdOut.println("hey!");} }'
    # text = 'import edu.princeton.cs.algs4.StdOut; public class new_test { public static void main(String[] args) { System.err.println("Hi"); System.out.println("Bye"); StdOut.println("hey!");} }'
    output, error = run_code_full(text, True)
    return jsonify("Standard Output:\n" + output, "Standard Error:\n" + error)


def run_code_full(text, is_algs4):
    class_name = text[text.find("class ")+6:text.find("{")-1]
    if not (class_name and text.find("class") >= 0 and text.find("{") >= 0):
        return "", "A Java program must have a class and a class name"

    myargs = (text, class_name, is_algs4)
    job = q.enqueue(run_code_in_command_line, args=myargs)
    while job.result is None:
        continue
    output, error = job.result
    return output, error


def run_code_in_command_line(code_text, class_name, is_algs4) -> (str, str):
    """ Do not name class_name with .java """
    import os
    import tempfile
    dir_path = tempfile.mkdtemp()
    stdoutPath = dir_path + "/out.txt"
    stderrPath = dir_path + "/err.txt"
    classPath = dir_path + "/" + class_name
    with open(classPath + ".java", "w") as code:
        code.write(code_text)

    def cleanup():
        os.system("rm -r " + dir_path)

    def compile():
        compile_command = "javac"
        if is_algs4:
            compile_command += " -cp .:./static/algs4/algs4.jar"
        os.system(compile_command + " " + classPath +
                  ".java" " 2> " + stderrPath)

    def execute():
        execute_command = "java"
        java_CLASSPATH = dir_path
        if is_algs4:
            # print(url_for('static'))
            java_CLASSPATH += ":./static/algs4/algs4.jar"
            print(java_CLASSPATH)
        pipingAddition = " 1> " + stdoutPath + " 2> " + stderrPath
        os.system(execute_command + " -cp " + java_CLASSPATH + " " +
                  class_name + pipingAddition)

    out_contents = ""
    err_contents = ""
    compile()
    with open(stderrPath) as err:
        err_contents = err.read()
    if err_contents:
        print("Problem compiling")
    elif not err_contents:
        print("executing")
        execute()
        with open(stderrPath) as err, open(stdoutPath) as out:
            out_contents = out.read()
            err_contents = err.read()
    cleanup()
    out_contents = out_contents.replace(dir_path+"/", "")
    err_contents = err_contents.replace(dir_path+"/", "")
    print("Returning out:", out_contents)
    print("Returning err:", err_contents)
    return out_contents, err_contents


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
