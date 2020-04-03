from flask import Flask, request, render_template, url_for
import flask_bootstrap
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
    os.system('javac tester.java')
    os.system('java tester')
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
@app.route('/run_code')
# def run_code(text, is_algs4 = False):
def run_code():
    text = 'public class test { public static void main(String[] args) { System.err.println("Hi") System.out.println("Bye") } }'
    class_name = "test"
    is_algs4 = False
    # code_file = tempfile.NamedTemporaryFile(delete=False).name
    # with open(code_file, "w") as code:
    #     code.write(text)
    output, error = q.enqueue(run_code_in_command_line,
                              args=(text, class_name, is_algs4))
    # os.system("rm -f " + code_file)
    return output


def run_code_in_command_line(code_text, class_name, is_algs4) -> (str, str):
    """ Do not name class_name with .java """
    import os
    import tempfile
    dir_path = tempfile.mkdtemp()
    stdoutPath = dir_path + "/out.txt"
    stderrPath = dir_path + "/err.txt"
    classPath = dir_path + "/" + class_name
    with open(classPath, "w") as code:
        code.write(code_text)

    compile_command = "javac"
    execute_command = "java"
    if is_algs4:
        compile_command = "javac-algs4"
        execute_command = "java"

    pipingAddition = " 1> " + stdoutPath + " 2> " + stderrPath
    compile_command = compile_command + " " + class_name + ".java" + pipingAddition
    execute_command = execute_command + " " + class_name + pipingAddition
    cleanup_command = "rm -r " + dir_path

    out_contents = ""
    err_contents = ""
    # compiling
    print("Running command:", compile_command)
    os.system(compile_command)
    with open(stderrPath) as err:
        err_contents = err.read()
    if err_contents:
        print("Running command:", cleanup_command)
        os.system(cleanup_command)
        return "", err_contents

    # executing
    print("Running command:", execute_command)
    os.system(execute_command)
    with open(stderrPath) as err, open(stdoutPath) as out:
        out_contents = out.read()
        err_contents = err.read()
    print("Running command:", cleanup_command)
    os.system(cleanup_command)
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
