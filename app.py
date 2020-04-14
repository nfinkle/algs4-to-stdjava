from flask import Flask, request, render_template, url_for, jsonify
# import flask_bootstrap
import worker
import rq
import time
# from flask_cors import CORS

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
    progress = {"print": 50, "scanner": 28, "else": 15}
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


def _compile_with_dir(class_path: str, dir_path: str, is_algs4: bool) -> str:
    """ Returns the compile output (error) for compiling text."""
    import os
    stderrPath = dir_path + "/compile_err.txt"
    compile_command = "javac"
    if is_algs4:
        compile_command += " -cp .:./static/algs4/algs4.jar"
    os.system(compile_command + " " + class_path + ".java" " 2> " + stderrPath)
    compile_output = open(stderrPath)
    return _cleanup_stderr(compile_output.read(), dir_path)


def _cleanup_stderr(stderr: str, dir_path: str) -> str:
    stderr = stderr.replace(
        "Picked up JAVA_TOOL_OPTIONS: -Xmx300m -Xss512k -XX:CICompilerCount=2 -Dfile.encoding=UTF-8 \n", "")
    return _remove_dir_path(stderr, dir_path)


def _remove_dir_path(contents: str, dir_path: str) -> str:
    return contents.replace(dir_path+"/", "")


def _execute_with_dir(class_name: str, dir_path: str, is_algs4: bool) -> (str, str):
    import os
    stdoutPath = dir_path + "/out.txt"
    stderrPath = dir_path + "/err.txt"
    java_CLASSPATH = dir_path
    if is_algs4:
        java_CLASSPATH += ":./static/algs4/algs4.jar"
    pipingAddition = " 1> " + stdoutPath + " 2> " + stderrPath
    os.system("java -cp " + java_CLASSPATH + " " + class_name + pipingAddition)
    err = open(stderrPath)
    out = open(stdoutPath)
    out_contents = _remove_dir_path(out.read(), dir_path)
    err_contents = _cleanup_stderr(err.read(), dir_path)
    return out_contents, err_contents


q = rq.Queue(connection=worker.conn)
@app.route('/run_code')
def run_code():
    text = request.args["code"]
    is_algs4 = request.args.get("is_algs4", False)
    print("is_algs4 =", is_algs4, "\ntext:\n" + text)
    result = _execute_code(text, is_algs4)
    print(result)
    if result is None:
        return jsonify("", "Timeout error. Code took too long to run.")
    return jsonify(result)


@app.route('/run_code_example')
def run_code_example():
    text = 'import edu.princeton.cs.algs4.StdOut; import edu.princeton.cs.algs4.Out; public class new_test { public static void main(String[] args) { StdOut.println("hey!"); Out stderr = new Out(System.err); stderr.println("I am in stderr"); } }'
    return jsonify(_execute_code(text, True))
    # return jsonify("Standard Output:\n" + output, "Standard Error:\n" + error)


@app.route('/compile_code')
def compile_code():
    text = request.args["code"]
    is_algs4 = request.args.get("is_algs4", False)
    print("is_algs4 =", is_algs4, "\ntext:\n" + text)
    return jsonify(_compile_code(text, is_algs4))


def _get_class_name(text: str) -> str:
    return text[text.find("class ")+6:text.find("{")-1]


def _execute_code(text: str, is_algs4: bool) -> (str, str):
    class_name = _get_class_name(text)
    if not (class_name and _is_valid_Java_program(text)):
        return "", "A Java program must have a class and a class name."

    myargs = (text, class_name, is_algs4)
    return _send_job_to_queue(_run_code_in_command_line, myargs)


def _is_valid_Java_program(code_text: str) -> bool:
    return code_text.find("class") >= 0 and code_text.find("{") >= 0


def _compile_code(code_text: str, is_algs4: bool) -> str:
    class_name = _get_class_name(code_text)
    if not (class_name and _is_valid_Java_program(code_text)):
        return "A Java program must have a class and a class name."

    myargs = (code_text, class_name, is_algs4)
    result = _send_job_to_queue(_compile_code_in_command_line, myargs)
    return "Timeout error. Code took too long to run." if result is None else result


def _compile_code_in_command_line(code_text, class_name, is_algs4) -> str:
    import os
    import tempfile
    dir_path = tempfile.mkdtemp()
    class_path = dir_path + "/" + class_name
    with open(class_path + ".java", "w") as code:
        code.write(code_text)
    err_output = _compile_with_dir(class_path, dir_path, is_algs4)
    os.system("rm -r " + dir_path)
    return err_output


def _send_job_to_queue(fn, myargs):
    job = q.enqueue(fn, args=myargs)
    start = time.time()
    while job.result is None and time.time() - start < 10:
        continue
    return job.result


def _run_code_in_command_line(code_text: str, class_name: str, is_algs4: bool) -> (str, str):
    """ Do not name class_name with .java """
    import os
    import tempfile
    dir_path = tempfile.mkdtemp()
    classPath = dir_path + "/" + class_name
    with open(classPath + ".java", "w") as code:
        code.write(code_text)

    out_contents = ""
    err_contents = _compile_with_dir(classPath, dir_path, is_algs4)
    if not err_contents:
        print("Compiled successfully.")
        out_contents, err_contents = _execute_with_dir(
            class_name, dir_path, is_algs4)
    print("Returning out:", out_contents)
    print("Returning err:", err_contents)
    os.system("rm -r " + dir_path)
    return out_contents, err_contents


@app.route('/code_base.html')
def show_code_base():
    code_text = """import java.util.LinkedList;

public class tester {
    public static void main(String[] args) {
        LinkedList<Integer> h = new LinkedList<Integer>();
		h.add(0);
		for (Integer i : h) {
		    System.out.println(i);
		}
	}
}"""
    sample_stdjava = """import java.util.LinkedList;
public class tester {
	public static void main(String[] args) {
		LinkedList<Integer> h = new LinkedList<Integer>();
		h.add(0);
		h.add(1);
		h.add(2);
		h.add(3);
		h.add(4);
		h.add(5);
		h.add(6);
		h.add(7);
		for (Integer i : h) {
			System.out.println(i);
		}
	}
}"""
    return render_template('code_pages/code_base.html', is_about=False, algs4_content=code_text, sample_stdjava=sample_stdjava)


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
