from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, url_for, jsonify, abort
import worker
import rq
import time
import os
import re
from flask_restx import inputs
from static.CASClient import CASClient

app = Flask(__name__)
app.secret_key = os.urandom(64)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://eqighedetevtqm:9f9d876d4536a1b08149955e1cbcb99728fae9fb87d654926fe778b8e8579012@ec2-34-230-149-169.compute-1.amazonaws.com:5432/ddkjho4mv302pc"
db = SQLAlchemy(app)
SQLALCHEMY_TRACK_MODIFICATIONS = False


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


def _getProgress(user):
    progress = {}

    def getPercentage(viewed, test_viewed, test_completed):
        return (viewed + test_viewed + test_completed * 2) * 25
    progress['system_out'] = getPercentage(
        user.system_out_viewed, user.system_out_test_viewed, user.system_out_test_completed)
    progress['scanner'] = getPercentage(
        user.scanner_viewed, user.scanner_test_viewed,  user.scanner_test_completed)
    progress['printwriter'] = getPercentage(
        user.printwriter_viewed, user.printwriter_test_viewed,  user.printwriter_test_completed)
    progress['hashmap'] = getPercentage(
        user.hashmap_viewed, user.hashmap_test_viewed,  user.hashmap_test_completed)
    progress['hashset'] = getPercentage(
        user.hashset_viewed, user.hashset_test_viewed,  user.hashset_test_completed)
    progress['treemap'] = getPercentage(
        user.treemap_viewed, user.treemap_test_viewed,  user.treemap_test_completed)
    progress['queue'] = getPercentage(
        user.queue_viewed, user.queue_test_viewed,  user.queue_test_completed)
    progress['priorityqueue'] = getPercentage(
        user.priorityqueue_viewed, user.priorityqueue_test_viewed,  user.priorityqueue_test_completed)
    progress['stack'] = getPercentage(
        user.stack_viewed, user.stack_test_viewed,  user.stack_test_completed)
    return progress


@app.route('/index.html')
def show_index():
    user = _getUser(CASClient().authenticate())
    progress = _getProgress(user)
    progressBars = {}
    for key, val in progress.items():
        progressBars[key] = "<div class='progress-bar' role='progressbar' style='width: " + \
            str(val) + "%' aria-valuenow='" + str(val) + \
            "%' aria-valuemin='0' aria-valuemax='100'> </div>"
    return render_template('index.html', is_about=False, progressBars=progressBars)


@app.route('/modules/system-out/APIs.html')
def show_system_out():
    user = _getUser(CASClient().authenticate())
    user.system_out_viewed = True
    db.session.commit()
    return render_template('modules/system-out.html', is_about=False, constructors=False)


@app.route('/modules/scanner/APIs.html')
def show_scanner():
    user = _getUser(CASClient().authenticate())
    user.scanner_viewed = True
    db.session.commit()
    if user.is_eval:
        return render_template("eval_modules/scanner.html", is_about=False, constructors=True)
    return render_template('modules/scanner.html', is_about=False, constructors=True)


@app.route('/modules/printwriter/APIs.html')
def show_printwriter():
    user = _getUser(CASClient().authenticate())
    user.printwriter_viewed = True
    db.session.commit()
    return render_template('modules/printwriter.html', is_about=False, constructors=True)


@app.route('/modules/hashmap/APIs.html')
def show_hashmap():
    user = _getUser(CASClient().authenticate())
    user.hashmap_viewed = True
    db.session.commit()
    if user.is_eval:
        return render_template("eval_modules/hashmap.html", is_about=False, constructors=True)
    return render_template('modules/hashmap.html', is_about=False, constructors=True)


@app.route('/modules/hashset/APIs.html')
def show_hashset():
    user = _getUser(CASClient().authenticate())
    user.hashset_viewed = True
    db.session.commit()
    return render_template('modules/hashset.html', is_about=False, constructors=True)


@app.route('/modules/treemap/APIs.html')
def show_treemap():
    user = _getUser(CASClient().authenticate())
    user.treemap_viewed = True
    db.session.commit()
    return render_template('modules/treemap.html', is_about=False, constructors=True)


@app.route('/modules/priorityqueue/APIs.html')
def show_priorityqueue():
    user = _getUser(CASClient().authenticate())
    user.priorityqueue_viewed = True
    db.session.commit()
    return render_template('modules/priorityqueue.html', is_about=False, constructors=True)


@app.route('/modules/queue/APIs.html')
def show_queue():
    user = _getUser(CASClient().authenticate())
    user.queue_viewed = True
    db.session.commit()
    if user.is_eval and user.is_groupA:
        return render_template("eval_modules/queue.html", is_about=False, constructors=True)
    return render_template('modules/queue.html', is_about=False, constructors=True)


@app.route('/modules/stack/APIs.html')
def show_stack():
    user = _getUser(CASClient().authenticate())
    user.stack_viewed = True
    db.session.commit()
    return render_template('modules/stack.html', is_about=False, constructors=True)


@app.route('/about_auth.html')
def show_about_auth():
    CASClient().authenticate()
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


def _initSecurity(dir_path: str, algs4_path="") -> (str, str):
    policy_name = "security_policy_that_I_hope_works.policy"
    if os.path.isfile(policy_name):
        raise ValueError("file exists already")
    # policy = "grant {\n\tpermission java.io.FilePermission \"" + dir_path + "/-\", \"read, write\";\n\tpermission java.io.FilePermission \"" + \
    #     algs4_path + "\", \"read,write\";\n};"
    policy = "grant {\n\tpermission java.io.FilePermission \"./-\", \"read, write\";"
    if algs4_path:
        policy += "\n\tpermission java.io.FilePermission \"" + \
            algs4_path + "\", \"read\";"
    policy += "\n};"
    with open(dir_path + "/" + policy_name, "w") as f:
        f.write(policy)
    return policy_name


def _addQuotesToPath(full_path: str) -> str:
    dirs = full_path.split("/")
    for i in range(len(dirs)):
        if ' ' in dirs[i]:
            dirs[i] = "'" + dirs[i] + "'"
    return '/'.join(dirs)


def _execute_with_dir(class_name: str, dir_path: str, is_algs4: bool, command_args: str, stdinPath: str) -> (str, str):
    import os
    stdoutPath = dir_path + "/out.txt"
    stderrPath = dir_path + "/err.txt"
    classpathOption = ""
    securityOption = "-Djava.security.manager -Djava.security.policy="
    # securityOption = "-Djava.security.manager -Djava.security.debug=access,failure -Djava.security.policy="
    if is_algs4:
        full_path = _addQuotesToPath(os.getcwd())
        algs4_path = full_path + "/static/algs4/algs4.jar"
        classpathOption = " -classpath .:" + algs4_path + " "
        securityOption += _initSecurity(dir_path, algs4_path) + " "
    else:
        securityOption += _initSecurity(dir_path) + " "
    pipingAddition = " < " + stdinPath + " 1> " + stdoutPath + " 2> " + stderrPath
    full_command = "cd " + dir_path + "; java " + securityOption + \
        classpathOption + class_name + " " + command_args + pipingAddition
    # full_command = "cd " + dir_path + "; java " + securityOption + " -cp " + \
    #     java_CLASSPATH + " " + class_name + " " + command_args + pipingAddition
    os.system(full_command)
    err = open(stderrPath)
    out = open(stdoutPath)
    out_contents = _remove_dir_path(out.read(), dir_path)
    err_contents = _cleanup_stderr(err.read(), dir_path)
    return out_contents, err_contents


q = rq.Queue(connection=worker.conn)
@app.route('/run_code')
def run_code():
    text = request.args["code"]
    is_algs4 = request.args.get("is_algs4", default=False, type=inputs.boolean)
    command_args = request.args.get("args", "")
    stdin = request.args.get("stdin", "")
    _validate_username(request.args["username"])
    result = _execute_code(text, is_algs4, command_args, stdin)
    if result is None:
        return jsonify("", "Timeout error. Code took too long to run.")
    return jsonify(result)


def _validate_username(username):
    q = DB_Entry.query.filter(DB_Entry.netid == username).one_or_none()
    if q is None:
        print("User", username, "not found")
        abort(404)
    return q


def stripErrLineNum(err):
    split = re.split(".java:[0-9]+", err)
    return '.java:_'.join(split)


@app.route('/mark_test_success')
def mark_success():
    module = request.args["module"]
    code = request.args["code"]
    username = request.args["username"]
    user = _getUser(username)
    print("Marking success for user", user.netid,
          "and module", module, ", and the code:")
    print(code)
    _mark_success_with_user_code(user, code, module)
    db.session.commit()
    return "Success!"


def _mark_success_with_user_code(user, code, module):
    if module == 'System.out/err':
        user.system_out_test_completed = True
    elif module == 'Scanner':
        user.scanner_test_completed = True
    elif module == 'PrintWriter':
        user.printwriter_test_completed = True
    elif module == 'HashMap':
        user.hashmap_test_completed = True
    elif module == 'HashSet':
        user.hashset_test_completed = True
    elif module == 'TreeMap':
        user.treemap_test_completed = True
    elif module == 'LinkedList':
        user.queue_test_completed = True
    elif module == 'PriorityQueue':
        user.priorityqueue_test_completed = True
    elif module == 'Stack':
        user.stack_test_completed = True
    else:
        abort(404)


def _save_code(user, code, module):
    if module == 'System.out/err':
        user.system_out_test_code = code
    elif module == 'Scanner':
        user.scanner_test_code = code
    elif module == 'PrintWriter':
        user.printwriter_test_code = code
    elif module == 'HashMap':
        user.hashmap_test_code = code
    elif module == 'HashSet':
        user.hashset_test_code = code
    elif module == 'TreeMap':
        user.treemap_test_code = code
    elif module == 'LinkedList':
        user.queue_test_code = code
    elif module == 'PriorityQueue':
        user.priorityqueue_test_code = code
    elif module == 'Stack':
        user.stack_test_code = code
    else:
        abort(404)
    db.session.commit()


@app.route('/get_diff', methods=['POST'])
def get_diff():
    args = request.get_json()
    _validate_username(args["username"])
    algs4_code = args["algs4_code"]
    stdjava_code = args["stdjava_code"]
    command_args = args.get("args", "")
    stdin = args.get("stdin", "")
    algs4_result = _execute_code(algs4_code, True, command_args, stdin)
    stdjava_result = _execute_code(stdjava_code, False, command_args, stdin)
    if algs4_result is None:
        algs4_out = ""
        algs4_err = "Timeout error. Code took too long to run."
    else:
        algs4_out, algs4_err = algs4_result
    if stdjava_result is None:
        stdjava_out = ""
        stdjava_err = "Timeout error. Code took too long to run."
    else:
        stdjava_out, stdjava_err = stdjava_result
    myargs = (algs4_out, stdjava_out)
    out_diff = _send_job_to_queue(_get_diff_command_line, myargs)
    myargs = (algs4_err, stdjava_err)
    err_diff = _send_job_to_queue(_get_diff_command_line, myargs)
    return jsonify(out_diff, err_diff)


def _get_diff_command_line(algs4: str, stdjava: str) -> str:
    import os
    import tempfile
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
    return out_contents


@app.route('/compile_code')
def compile_code():
    text = request.args["code"]
    module = request.args["module"]
    is_algs4 = request.args.get("is_algs4", default=False, type=inputs.boolean)
    user = _validate_username(request.args["username"])
    print("is_algs4 =", is_algs4, "\ntext:\n" + text)
    return jsonify(_compile_code(text, is_algs4, user, module))


def _get_class_name(text: str) -> str:
    return text[text.find("class ")+6:text.find("{")-1]


def _execute_code(text: str, is_algs4: bool, command_args: str, stdin: str) -> (str, str):
    myargs = (text, is_algs4, command_args, stdin)
    return _send_job_to_queue(_run_code_in_command_line, myargs)


def _is_valid_Java_program(code_text: str) -> bool:
    return code_text.find("class") >= 0 and code_text.find("{") >= 0


def _compile_code(code_text: str, is_algs4: bool, user, module: str) -> str:
    class_name = _get_class_name(code_text)
    if not (class_name and _is_valid_Java_program(code_text)):
        return "A Java program must have a class and a class name."

    def save_code_fn():
        _save_code(user, code_text, module)

    myargs = (code_text, class_name, is_algs4)
    result = _send_job_to_queue(
        _compile_code_in_command_line, myargs, save_code_fn=save_code_fn)
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


def _send_job_to_queue(fn, myargs, save_code_fn=None):
    job = q.enqueue(fn, args=myargs, result_ttl=10)
    start = time.time()
    if save_code_fn is not None:
        save_code_fn()
    while job.result is None and time.time() - start < 10:
        continue
    return job.result


def _run_code_in_command_line(code_text: str, is_algs4: bool, command_args: str, stdin: str) -> (str, str):
    import os
    import tempfile
    class_name = _get_class_name(code_text)
    if not (class_name and _is_valid_Java_program(code_text)):
        return "", "A Java program must have a class and a class name."

    dir_path = tempfile.mkdtemp()
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
        with open(stdinPath, "w") as stdin_file:
            stdin_file.write(stdin)
        out_contents, err_contents = _execute_with_dir(
            class_name, dir_path, is_algs4, command_args, stdinPath)

    print("Returning out:", out_contents)
    print("Returning err:", err_contents)
    os.system("rm -r " + dir_path)
    return out_contents, err_contents


@app.route('/modules/stack/test.html')
def show_stack_test():
    user = _getUser(CASClient().authenticate())
    user.stack_test_viewed = True
    db.session.commit()
    return render_template("code_pages/stack.html", is_about=False, stdjava_code=user.stack_test_code, username=user.netid)


@app.route('/modules/priorityqueue/test.html')
def show_priorityqueue_test():
    user = _getUser(CASClient().authenticate())
    user.priorityqueue_test_viewed = True
    db.session.commit()
    return render_template("code_pages/priorityqueue.html", is_about=False, stdjava_code=user.priorityqueue_test_code, username=user.netid)


@app.route('/modules/queue/test.html')
def show_queue_test():
    user = _getUser(CASClient().authenticate())
    user.queue_test_viewed = True
    db.session.commit()
    return render_template("code_pages/queue.html", is_about=False, stdjava_code=user.queue_test_code, username=user.netid)


@app.route('/modules/treemap/test.html')
def show_treemap_test():
    user = _getUser(CASClient().authenticate())
    user.treemap_test_viewed = True
    db.session.commit()
    return render_template("code_pages/treemap.html", is_about=False, stdjava_code=user.treemap_test_code, username=user.netid)


@app.route('/modules/hashmap/test.html')
def show_hashmap_test():
    user = _getUser(CASClient().authenticate())
    user.hashmap_test_viewed = True
    db.session.commit()
    return render_template("code_pages/hashmap.html", is_about=False, stdjava_code=user.hashmap_test_code, username=user.netid)


@app.route('/modules/printwriter/test.html')
def show_printwriter_test():
    user = _getUser(CASClient().authenticate())
    user.printwriter_test_viewed = True
    db.session.commit()
    return render_template("code_pages/printwriter.html", is_about=False, stdjava_code=user.printwriter_test_code, username=user.netid)


@app.route('/modules/system-out/test.html')
def show_system_out_test():
    user = _getUser(CASClient().authenticate())
    user.system_out_test_viewed = True
    db.session.commit()
    return render_template("code_pages/system-out.html", is_about=False, stdjava_code=user.system_out_test_code, username=user.netid)


@app.route('/modules/hashset/test.html')
def show_hashset_test():
    user = _getUser(CASClient().authenticate())
    user.hashset_test_viewed = True
    db.session.commit()
    return render_template("code_pages/hashset.html", is_about=False, stdjava_code=user.hashset_test_code, username=user.netid)


@app.route('/modules/scanner/test.html')
def show_scanner_test():
    user = _getUser(CASClient().authenticate())
    user.scanner_test_viewed = True
    db.session.commit()
    return render_template("code_pages/scanner.html", is_about=False, stdjava_code=user.scanner_test_code, username=user.netid)


@app.route('/about.html')
def show_about_unauth():
    return render_template('about_unauth.html', is_about=True)


class DB_Entry(db.Model):
    # __tablename__ = 'users'

    netid = db.Column(db.String, primary_key=True)
    system_out_viewed = db.Column(db.Boolean)
    system_out_test_viewed = db.Column(db.Boolean)
    system_out_test_completed = db.Column(db.Boolean)
    system_out_test_code = db.Column(db.String)
    scanner_viewed = db.Column(db.Boolean)
    scanner_test_viewed = db.Column(db.Boolean)
    scanner_test_completed = db.Column(db.Boolean)
    scanner_test_code = db.Column(db.String)
    printwriter_viewed = db.Column(db.Boolean)
    printwriter_test_viewed = db.Column(db.Boolean)
    printwriter_test_completed = db.Column(db.Boolean)
    printwriter_test_code = db.Column(db.String)
    hashmap_viewed = db.Column(db.Boolean)
    hashmap_test_viewed = db.Column(db.Boolean)
    hashmap_test_completed = db.Column(db.Boolean)
    hashmap_test_code = db.Column(db.String)
    hashset_viewed = db.Column(db.Boolean)
    hashset_test_viewed = db.Column(db.Boolean)
    hashset_test_completed = db.Column(db.Boolean)
    hashset_test_code = db.Column(db.String)
    treemap_viewed = db.Column(db.Boolean)
    treemap_test_viewed = db.Column(db.Boolean)
    treemap_test_completed = db.Column(db.Boolean)
    treemap_test_code = db.Column(db.String)
    priorityqueue_viewed = db.Column(db.Boolean)
    priorityqueue_test_viewed = db.Column(db.Boolean)
    priorityqueue_test_completed = db.Column(db.Boolean)
    priorityqueue_test_code = db.Column(db.String)
    stack_viewed = db.Column(db.Boolean)
    stack_test_completed = db.Column(db.Boolean)
    stack_test_code = db.Column(db.String)
    stack_test_viewed = db.Column(db.Boolean)
    queue_viewed = db.Column(db.Boolean)
    queue_test_viewed = db.Column(db.Boolean)
    queue_test_completed = db.Column(db.Boolean)
    queue_test_code = db.Column(db.String)
    is_eval = db.Column(db.Boolean)
    is_groupA = db.Column(db.Boolean)

    def __init__(self, username):
        empty_class = """// standard java imports here (e.g. import java.util.ArrayList;)
public class tester {
   public static void main(String[] args) {
      throw new UnsupportedOperationException(\"Unimplemented method.\");
   }
}"""
        self.netid = username
        self.system_out_viewed = False
        self.system_out_test_viewed = False
        self.system_out_test_completed = False
        self.system_out_test_code = empty_class
        self.scanner_viewed = False
        self.scanner_test_viewed = False
        self.scanner_test_completed = False
        self.scanner_test_code = empty_class
        self.printwriter_viewed = False
        self.printwriter_test_viewed = False
        self.printwriter_test_completed = False
        self.printwriter_test_code = empty_class
        self.hashmap_viewed = False
        self.hashmap_test_viewed = False
        self.hashmap_test_completed = False
        self.hashmap_test_code = empty_class
        self.hashset_viewed = False
        self.hashset_test_viewed = False
        self.hashset_test_completed = False
        self.hashset_test_code = empty_class
        self.treemap_viewed = False
        self.treemap_test_viewed = False
        self.treemap_test_completed = False
        self.treemap_test_code = empty_class
        self.priorityqueue_viewed = False
        self.priorityqueue_test_viewed = False
        self.priorityqueue_test_completed = False
        self.priorityqueue_test_code = empty_class
        self.stack_viewed = False
        self.stack_test_completed = False
        self.stack_test_code = empty_class
        self.stack_test_viewed = False
        self.queue_viewed = False
        self.queue_test_viewed = False
        self.queue_test_completed = False
        self.queue_test_code = empty_class
        self.is_eval = False
        self.is_groupA = False


def _getUser(username: str) -> DB_Entry:
    q = DB_Entry.query.filter(DB_Entry.netid == username).one_or_none()
    if not q:
        print("Creating new user!")
        db.session.add(DB_Entry(username))
        db.session.commit()
        q = DB_Entry.query.filter(DB_Entry.netid == username).one()
    return q


@app.route('/mark_eval_groupA')
def mark_eval_groupA():
    user = _getUser(CASClient().authenticate())
    user.is_eval = True
    user.is_groupA = True
    db.session.commit()
    return show_index()


@app.route('/mark_eval_groupB')
def mark_eval_groupB():
    user = _getUser(CASClient().authenticate())
    user.is_eval = True
    user.is_groupA = False
    db.session.commit()
    return show_index()


@app.route('/remove_from_eval')
def remove_from_eval():
    username = request.args["username"] + '\n'
    user = _getUser(username)
    user.is_eval = False
    db.session.commit()
    print("removing", username, "from eval")
    return show_index()


@app.errorhandler(404)
def handle_bad_request(e):
    print(e.description)
    return render_template('404_error.html', e=e.description), 404


if __name__ == "__main__":
    app.run(debug=True, development=True)
    show_index()
