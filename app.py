from flask import Flask, request, render_template, url_for, jsonify
import worker
import rq
import time
import os
import re
from flask_restx import inputs
from static.CASClient import CASClient

app = Flask(__name__)
app.secret_key = os.urandom(64)


@app.route('/logout')
def logout():
    casClient = CASClient()
    casClient.authenticate()
    casClient.logout()
    return show_home()


@app.route('/health', methods=['GET'])
def health():
    return "I'm online"


@app.route('/')
@app.route('/home')
@app.route('/home.html')
def show_home():
    return render_template('home.html', is_about=False)


@app.route('/index.html')
def show_index():
    username = CASClient().authenticate()
    progress = {"print": 50, "scanner": 28, "else": 15}
    progressBars = {}
    for key, val in progress.items():
        progressBars[key] = "<div class='progress-bar' role='progressbar' style='width: " + \
            str(val) + "%' aria-valuenow='" + str(val) + \
            "%' aria-valuemin='0' aria-valuemax='100'> </div>"
    return render_template('index.html', is_about=False, progressBars=progressBars)


@app.route('/modules/module.html')
def show_module():
    username = CASClient().authenticate()
    return render_template('modules/module.html', is_about=False, constructors=True)


@app.route('/modules/system-out/APIs.html')
def show_system_out():
    username = CASClient().authenticate()
    return render_template('modules/system-out.html', is_about=False, constructors=False)


@app.route('/modules/scanner/APIs.html')
def show_scanner():
    username = CASClient().authenticate()
    return render_template('modules/scanner.html', is_about=False, constructors=True)


@app.route('/modules/printwriter/APIs.html')
def show_printwriter():
    username = CASClient().authenticate()
    return render_template('modules/printwriter.html', is_about=False, constructors=True)


@app.route('/modules/hashmap/APIs.html')
def show_hashmap():
    username = CASClient().authenticate()
    return render_template('modules/hashmap.html', is_about=False, constructors=True)


@app.route('/modules/hashset/APIs.html')
def show_hashset():
    username = CASClient().authenticate()
    return render_template('modules/hashset.html', is_about=False, constructors=True)


@app.route('/modules/treemap/APIs.html')
def show_treemap():
    username = CASClient().authenticate()
    return render_template('modules/treemap.html', is_about=False, constructors=True)


@app.route('/modules/priorityqueue/APIs.html')
def show_priorityqueue():
    username = CASClient().authenticate()
    return render_template('modules/priorityqueue.html', is_about=False, constructors=True)


@app.route('/modules/queue/APIs.html')
def show_queue():
    username = CASClient().authenticate()
    return render_template('modules/queue.html', is_about=False, constructors=True)


@app.route('/modules/stack/APIs.html')
def show_stack():
    username = CASClient().authenticate()
    return render_template('modules/stack.html', is_about=False, constructors=True)


@app.route('/about_auth.html')
def show_about_auth():
    username = CASClient().authenticate()
    return render_template('about_auth.html', is_about=True)


def _compile_with_dir(class_path: str, dir_path: str, is_algs4: bool) -> str:
    """ Returns the compile output (error) for compiling text."""
    import os
    stderrPath = dir_path + "/compile_err.txt"
    compile_command = "javac -classpath " + dir_path + "/*"
    if is_algs4:
        compile_command += ":./static/algs4/algs4.jar"
    os.system(compile_command + " " + class_path + ".java" " 2> " + stderrPath)
    compile_output = open(stderrPath)
    return _cleanup_stderr(compile_output.read(), dir_path)


def _cleanup_stderr(stderr: str, dir_path: str) -> str:
    stderr = stderr.replace(
        "Picked up JAVA_TOOL_OPTIONS: -Xmx300m -Xss512k -XX:CICompilerCount=2 -Dfile.encoding=UTF-8 \n", "")
    return _remove_dir_path(stderr, dir_path)


def _remove_dir_path(contents: str, dir_path: str) -> str:
    return contents.replace(dir_path+"/", "")


def _initSecurity(dir_path: str) -> (str, str):
    policy_name = "security_policy_that_I_hope_works.policy"
    if os.path.isfile(policy_name):
        raise ValueError("file exists already")
    policy = "grant {\n\tpermission java.io.FilePermission \"" + \
        dir_path + "/-\", \"read, write\";\n};"
    # policy = "grant codeBase \"file:" + dir_path + \
    #     "/-\" {\n\tpermission java.io.FilePermission \"*\", \"read\";\n\tpermission java.io.FilePermission \"*\", \"write\";\n};"
    with open(policy_name, "w") as f:
        print(policy)
        f.write(policy)
    return policy_name


def _addQuotesToPath(full_path: str) -> str:
    dirs = full_path.split("/")
    for i in range(len(dirs)):
        if ' ' in dirs[i]:
            dirs[i] = "\"" + dirs[i] + "\""
    return '/'.join(dirs)


def _execute_with_dir(class_name: str, dir_path: str, is_algs4: bool, command_args: str, stdinPath: str) -> (str, str):
    import os
    stdoutPath = dir_path + "/out.txt"
    stderrPath = dir_path + "/err.txt"
    java_CLASSPATH = dir_path
    args_string = ""
    securityOption = "-Djava.security.manager -Djava.security.policy="
    # securityOption = "-Djava.security.manager -Djava.security.debug=access,failure -Djava.security.policy="
    if is_algs4:
        full_path = _addQuotesToPath(os.getcwd())
        securityOption += full_path + '/'
        java_CLASSPATH += ":" + full_path + "/static/algs4/algs4.jar"
    pipingAddition = " < " + stdinPath + " 1> " + stdoutPath + " 2> " + stderrPath
    securityPolicyName = _initSecurity(dir_path)
    securityOption += securityPolicyName
    # securityOption = ""
    full_command = "cd " + dir_path + "; java " + securityOption + " -cp " + \
        java_CLASSPATH + " " + class_name + " " + command_args + pipingAddition
    print(full_command)
    os.system(full_command)
    err = open(stderrPath)
    out = open(stdoutPath)
    os.system("rm " + securityPolicyName)
    out_contents = _remove_dir_path(out.read(), dir_path)
    err_contents = _cleanup_stderr(err.read(), dir_path)
    return out_contents, err_contents


q = rq.Queue(connection=worker.conn)
@app.route('/run_code')
def run_code():
    CASClient().authenticate()
    text = request.args["code"]
    is_algs4 = request.args.get("is_algs4", default=False, type=inputs.boolean)
    command_args = request.args.get("args", "")
    stdin = request.args.get("stdin", "")
    print(stdin)
    result = _execute_code(text, is_algs4, command_args, stdin)
    if result is None:
        return jsonify("", "Timeout error. Code took too long to run.")
    return jsonify(result)


# @app.route('/run_code_example')
# def run_code_example():
#     text = 'import edu.princeton.cs.algs4.StdOut; import edu.princeton.cs.algs4.Out; public class new_test { public static void main(String[] args) { StdOut.println("hey!"); Out stderr = new Out(System.err); stderr.println("I am in stderr"); } }'
#     return jsonify(_execute_code(text, True, "", ""))


def stripErrLineNum(err):
    split = re.split(".java:[0-9]+", err)
    return '.java:_'.join(split)


@app.route('/get_diff')
def get_diff():
    CASClient().authenticate()
    algs4_out = request.args["algs4_out"]
    stdjava_out = request.args["stdjava_out"]
    algs4_err = stripErrLineNum(request.args.get("algs4_err", ""))
    stdjava_err = stripErrLineNum(request.args.get("stdjava_err", ""))
    myargs = (algs4_out, stdjava_out)
    out_diff = _send_job_to_queue(_get_diff_command_line, myargs)
    myargs = (algs4_err, stdjava_err)
    err_diff = _send_job_to_queue(_get_diff_command_line, myargs)
    return jsonify(out_diff, err_diff)


def _get_diff_command_line(algs4: str, stdjava: str) -> str:
    import os
    import tempfile
    print(algs4)
    print(stdjava)
    dir_path = tempfile.mkdtemp()
    algs4_path = dir_path + "/algs4.txt"
    stdjava_path = dir_path + "/stdjava.txt"
    out_path = dir_path + "/out.txt"
    with open(algs4_path, "w") as a4, open(stdjava_path, "w") as stdj:
        a4.write(algs4)
        stdj.write(stdjava)
    os.system("diff -y " + algs4_path + " " + stdjava_path + " > " + out_path)
    with open(out_path) as out:
        out_contents = out.read()
    os.system("rm -r " + dir_path)
    print(out_contents)
    return out_contents


@app.route('/compile_code')
def compile_code():
    CASClient().authenticate()
    text = request.args["code"]
    is_algs4 = request.args.get("is_algs4", default=False, type=inputs.boolean)
    print("is_algs4 =", is_algs4, "\ntext:\n" + text)
    return jsonify(_compile_code(text, is_algs4))


def _get_class_name(text: str) -> str:
    return text[text.find("class ")+6:text.find("{")-1]


def _execute_code(text: str, is_algs4: bool, command_args: str, stdin: str) -> (str, str):
    myargs = (text, is_algs4, command_args, stdin)
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
    print("Compiling:", code_text)
    with open(class_path + ".java", "w") as code:
        code.write(code_text)
    err_output = _compile_with_dir(class_path, dir_path, is_algs4)
    os.system("rm -r " + dir_path)
    return err_output


def _send_job_to_queue(fn, myargs):
    job = q.enqueue(fn, args=myargs, result_ttl=7)
    start = time.time()
    while job.result is None and time.time() - start < 7:
        continue
    return job.result


def _run_code_in_command_line(code_text: str, is_algs4: bool, command_args: str, stdin: str) -> (str, str):
    import os
    import tempfile
    class_name = _get_class_name(code_text)
    if not (class_name and _is_valid_Java_program(code_text)):
        return "", "A Java program must have a class and a class name."

    dir_path = tempfile.mkdtemp()
    print(dir_path)
    classPath = dir_path + "/" + class_name
    stdinPath = dir_path + "/in.txt"
    print("code = ", code_text)
    print("command_args =", command_args)
    print("stdin =", stdin)
    with open(classPath + ".java", "w") as code:
        code.write(code_text)

    out_contents = ""
    err_contents = _compile_with_dir(classPath, dir_path, is_algs4)
    if not err_contents:
        print("Compiled successfully.")
        with open(stdinPath, "w") as stdin_file:
            stdin_file.write(stdin)
        out_contents, err_contents = _execute_with_dir(
            class_name, dir_path, is_algs4, command_args, stdinPath)

    print("Returning out:", out_contents)
    print("Returning err:", err_contents)
    for fname in os.listdir(dir_path):
        if '.class' in fname or '.java' in fname:
            continue
        with open(dir_path + "/" + fname) as f:
            print("\"" + fname + "\" =", f.read())
    os.system("rm -r " + dir_path)
    return out_contents, err_contents


empty_class = """// standard java imports here
public class tester {
   public static void main(String[] args) {
      throw new UnsupportedOperationException(\"Unimplemented method.\");
   }
}"""


@app.route('/modules/stack/test.html')
def show_stack_test():
    username = CASClient().authenticate()
    return render_template("code_pages/stack.html", is_about=False, test_stdjava=empty_class)


@app.route('/modules/priorityqueue/test.html')
def show_priorityqueue_test():
    username = CASClient().authenticate()
    return render_template("code_pages/priorityqueue.html", is_about=False,  test_stdjava=empty_class)


@app.route('/modules/queue/test.html')
def show_queue_test():
    username = CASClient().authenticate()
    return render_template("code_pages/queue.html", is_about=False,  test_stdjava=empty_class)


@app.route('/modules/treemap/test.html')
def show_treemap_test():
    username = CASClient().authenticate()
    return render_template("code_pages/treemap.html", is_about=False,  test_stdjava=empty_class)


@app.route('/modules/hashmap/test.html')
def show_hashmap_test():
    username = CASClient().authenticate()
    return render_template("code_pages/hashmap.html", is_about=False,  test_stdjava=empty_class)


@app.route('/modules/printwriter/test.html')
def show_printwriter_test():
    username = CASClient().authenticate()
    return render_template("code_pages/printwriter.html", is_about=False,  test_stdjava=empty_class)


@app.route('/modules/system-out/test.html')
def show_system_out_test():
    username = CASClient().authenticate()
    return render_template("code_pages/system-out.html", is_about=False,  test_stdjava=empty_class)


@app.route('/modules/hashset/test.html')
def show_hashset_test():
    username = CASClient().authenticate()
    return render_template("code_pages/hashset.html", is_about=False,  test_stdjava=empty_class)


@app.route('/modules/scanner/test.html')
def show_scanner_test():
    username = CASClient().authenticate()
    return render_template("code_pages/scanner.html", is_about=False,  test_stdjava=empty_class)


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
