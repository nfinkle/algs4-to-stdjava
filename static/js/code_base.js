function compile() {
	var code = document.getElementById("code_form").elements[0].value;
	compile_with_code(code, getModule());
}

// This function displays the compiler error, but does not render the Prism output
function display_compile_error(compile_err) {
	var err_html = "";
	if (compile_err) {
		const pre_err_html = "<h4>  Compile Error</h4><pre class=\"line-numbers\" style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-javastacktrace match-braces\">";
		const post_err_html = "</code></pre>";
		err_html = pre_err_html + compile_err + post_err_html;
	}
	document.getElementById("algs4_output").innerHTML = err_html;
	return !compile_err;
}

function markSuccess(code, mod) {
	username = $('#username').data().other
	$.ajax({
		url: "/mark_test_success",
		async: true,
		cache: false,
		timeout: 30000,
		moreTries: 5,
		data: {
			"code": code,
			"module": mod,
			"username": username
		},
		error: function (xhr, textStatus, error) {
			console.log("trial = " + this.moreTries);
			if (textStatus == 'timeout') {
				this.moreTries--;
				if (this.moreTries > 0) {
					$.ajax(this);
					return;
				}
			}
		}
	})
}

function compile_with_code(code, mod) {
	$('button').prop("disabled", true)
	username = $('#username').data().other
	document.getElementById("algs4_output").innerHTML = "";
	$.ajax({
		url: "/compile_code",
		async: true,
		cache: false,
		timeout: 10000,
		moreTries: 15,
		data: {
			"code": code,
			"is_algs4": false,
			"username": username,
			"module": mod
		},
		error: function (xhr, textStatus, error) {
			console.log("trial = " + this.moreTries);
			if (textStatus == 'timeout') {
				this.moreTries--;
				if (this.moreTries > 0) {
					$.ajax(this);
					return;
				}
			}
		},
		success: function (result) {
			add_execute_button = display_compile_error(result)
			replaceFormWithPre(code, add_execute_button);
			Prism.highlightAll();
			$('button').prop("disabled", false)
		}
	})
}

function cleanupTests(raw) {
	// raw = eval($('#tests-data').data().other);
	for (i = 0; i < raw.length; i++) {
		raw[i]['arg'] = raw[i]['arg'].replace(/&quot/g, '\"');
		raw[i]['stdin'] = raw[i]['stdin'].replace(/&quot/g, '\"');
		raw[i]['out'][0] = raw[i]['out'][0].replace(/&quot/g, '\"');
		raw[i]['out'][1] = raw[i]['out'][1].replace(/&quot/g, '\"');
	}
	// console.log(typeof (raw));
	// return JSON.stringify(raw);
	return raw;
}

function replaceFormWithPre(code, add_execute_button) {
	var new_html = "<h3 class=\"text-center\">Standard Java Library</h3><pre class=\"line-numbers\" style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-java match-braces\">" + code.replace(/</g, "&lt").replace(/>/g, "&gt") + "</code></pre>" + "<button type=\"button\" class=\"btn btn-primary\" id=\"edit_btn\" onclick=\"edit()\">Edit</button>";
	if (add_execute_button) {
		new_html += "<button type = \"button\" class=\"btn btn-primary\" id=\"execute_btn\" onclick=execute()>Execute</button>";
		tests = $('#tests-data').data().other
		new_html += '<button type="button" class="btn btn-primary" onclick="compare_outputs()">Compare</button>'
		new_html += '<button type="button" class="btn btn-primary" onclick="run_tests(' + tests + ')">Run Tests</button>'
		new_html += "<button type=\"button\" class=\"btn btn-primary d-none\" data-toggle=\"modal\" data-target=\"#answer_code\" id=\"show_answer_btn\">Show Answer</button>"
	}
	document.getElementById("stdjava_code").innerHTML = new_html;
}

function getString(arr, start, n) {
	newString = ""
	for (i = 0; i < n; i++) {
		newString += arr[i + start];
	}
	return newString;
}

function getModule() {
	return $('#module').data().other
}

function extract_code_from_pre(id) {
	var cur_inner = document.getElementById(id).innerHTML;
	var tmp = cur_inner /*.replace(/\s\s/g, "")*/ .replace(/<button.*/g, "").replace(/Standard Java Library/, "");
	var code = "";
	for (var i = 0; i < tmp.length; i++) {
		var three = getString(tmp, i, 3);
		var four = three + tmp[i + 3];
		var five = four + tmp[i + 4];
		var six = five + tmp[i + 5];
		if (five == "<span" || six == "</span" || four == "<pre" || five == "<code" || five == "</pre" || six == "</code" || three == "<h3" || four == "</h3" || four == "<div" || five == "</div") {
			for (; i < tmp.length && tmp[i] != ">"; i++)
			;
			i++;
			for (; i < tmp.length && tmp[i] != "<"; i++) {
				code += tmp[i];
			}
			i--;
		} else {
			code += tmp[i];
		}
	}
	// tmp = corrected.replace(/<\/span>/, "\s");
	// console.log(tmp);
	// tmp = tmp.split(">");

	return code.replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/&amp;/g, "&");;
}

function edit() {
	$('button').prop("disabled", true)
	var code = extract_code_from_pre("stdjava_code");
	var lines = (code.match(/\n/g) || []).length
	var new_html_start = "<h3 class=\"text-center\">Standard Java Library</h3><form id=\"code_form\" spellcheck=\"false\"><p><textarea id=\"form_textarea\" style=\"font-size: 11px\"; rows=\"";
	var middle = lines + "\";>" + code
	var new_html_end = "</textarea>" + "<button type=\"button\" class=\"btn btn-primary\" onclick=\"compile()\">Compile</button></p></form>";
	var new_html = new_html_start + middle + new_html_end;
	document.getElementById("stdjava_code").innerHTML = new_html;
	$('button').prop("disabled", false)
}

function execute_from_code(code, is_algs4, command_args, stdin) {
	ret_fn = function (result) {
		$('button').prop("disabled", false);
		html = ""
		const post_html = "</code></pre>";
		if (result[0] || (!result[0] && !result[1])) {
			const pre_output_html = "<h4>Output</h4><pre  style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-javastacktrace match-braces\">";
			html += pre_output_html + result[0] + post_html;
		}
		if (result[1]) {
			const pre_err_html = "<h4>Error</h4><pre style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-javastacktrace match-braces\">";
			html += pre_err_html + result[1] + post_html;
		}

		document.getElementById("algs4_output").innerHTML = html;
		Prism.highlightAll();
	}
	send_exec_request(code, is_algs4, command_args, stdin, ret_fn)
}

function execute_algs4() {
	$('button').prop("disabled", true)
	document.getElementById("algs4_output").innerHTML = "";
	var code = extract_code_from_pre("algs4_code");
	var args = document.getElementById("command_args").value;
	var stdin = document.getElementById("stdin").value;
	execute_from_code(code, true, args, stdin);
}

function execute() {
	$('button').prop("disabled", true)
	document.getElementById("algs4_output").innerHTML = "";
	var code = extract_code_from_pre("stdjava_code");
	var args = document.getElementById("command_args").value;
	var stdin = document.getElementById("stdin").value;
	execute_from_code(code, false, args, stdin);
}

function send_exec_request(code, is_algs4, command_args, stdin, ret_fn) {
	username = $('#username').data().other
	$.ajax({
		url: "/run_code",
		async: true,
		timeout: 10000,
		moreTries: 10,
		cache: false,
		data: {
			"code": code,
			"is_algs4": is_algs4,
			"args": command_args,
			"stdin": stdin,
			"username": username
		},
		success: function (result) {
			ret_fn(result)
		},
		error: function (xhr, textStatus, error) {
			console.log("trial = " + this.moreTries);
			if (textStatus == 'timeout') {
				this.moreTries--;
				if (this.moreTries > 0) {
					$.ajax(this);
					return;
				}
			}
			$('button').prop("disabled", false)
			document.getElementById("algs4_output").innerHTML = "<h4>Tests</h4><pre style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-java\">There was some internal issue. Please contact the creator.</code></pre>";
			console.log(error);
		}
	})
}


function run_next_test(ith_test, result, code, test_list) {
	cur_html = document.getElementById("algs4_output").innerHTML.replace(/&gt;/g, ">").replace(/&lt;/g, "<")
	cur_html = cur_html.split("Running")[0]; // replace Running and pre closes
	cur_html += "Test " + ith_test + ": ";
	const desired_output = test_list[ith_test]["out"];
	result[1] = result[1].replace(/java:[0-9]+/g, "java:_");
	var nonSuccess = true;
	if (result[0].valueOf() === desired_output[0].valueOf() && result[1].valueOf() === desired_output[1].valueOf()) {
		cur_html += "Success!\n"
		nonSuccess = false;
	} else if (result[0].valueOf() === desired_output[0].valueOf()) {
		cur_html += "Correct output, but not error.\n"
		console.log("Received:\n" + result[1]);
		console.log("Desired:\n" + desired_output[1]);
	} else if (result[1].valueOf() === desired_output[1].valueOf() && (result[1] || desired_output[1])) {
		cur_html += "Correct error, but not output.\n"
	} else {
		console.log("Received:\n" + result[0]);
		console.log("Desired:\n" + desired_output[0]);
		cur_html += "Failed.\n"
	}
	if (ith_test < test_list.length - 1) {
		cur_html += "Running Test " + (ith_test + 1) + "\n";
		send_exec_request(code, false, test_list[ith_test + 1]["arg"], test_list[ith_test + 1]["stdin"], function (result) {
			run_next_test(ith_test + 1, result, code, test_list)
		})
	} else {
		$('button').prop("disabled", false);
		markSuccess(code, getModule);
		if (nonSuccess) {
			document.getElementById("trials").innerHTML += "I";
		}
		trials = document.getElementById("trials").innerHTML.split("").length;
		if (trials >= 5) {
			document.getElementById("show_answer_btn").className = "btn btn-primary"
		}
	}
	cur_html += "</code></pre>"
	document.getElementById("algs4_output").innerHTML = cur_html;
	Prism.highlightAll();
}

function run_tests(test_list) {
	test_list = cleanupTests(test_list);
	$('button').prop("disabled", true);
	var code = extract_code_from_pre("stdjava_code");
	document.getElementById("algs4_output").innerHTML = "<h4>Tests</h4><pre style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-java\">Running Test 0\n</code></pre>";
	Prism.highlightAll();
	send_exec_request(code, false, test_list[0]["arg"], test_list[0]["stdin"], function (result) {
		run_next_test(0, result, code, test_list);
	})
}


function show_diff(algs4_code, stdjava_code, args, stdin) {
	username = $('#username').data().other
	$.ajax({
		url: "/get_diff",
		type: "POST",
		contentType: 'application/json',
		dataType: 'json',
		async: true,
		cache: false,
		data: JSON.stringify({
			"args": args,
			"stdin": stdin,
			"username": username,
			"algs4_code": algs4_code,
			"stdjava_code": stdjava_code,
		}),
		moreTries: 15,
		timeout: 25000,
		error: function (xhr, textStatus, error) {
			console.log("trial = " + this.moreTries);
			if (textStatus == 'timeout') {
				this.moreTries--;
				if (this.moreTries > 0) {
					$.ajax(this);
					return;
				}
			}
			$('button').prop("disabled", false)
			document.getElementById("algs4_output").innerHTML = "<h4>Compare</h4><pre style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-java\">There was some internal issue. Please contact the creator.</code></pre>";
			Prism.highlightAll();
			console.log(error);
		},
		success: function (result) {
			html = ""
			const pre_html = "<pre style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-diff\">";
			const post_html = "</code></pre>";
			if (result[0] || (!result[0] && !result[1])) {
				const pre_out_html = "<h4>Outputs</h4>";
				html += pre_out_html + pre_html + result[0] + post_html;
			}
			if (result[1]) {
				const pre_err_html = "<h4>Errors</h4>";
				html += pre_err_html + pre_html + result[1] + post_html;
			}
			document.getElementById("algs4_output").innerHTML = html;
			Prism.highlightAll();
			$('button').prop("disabled", false)
		}
	})
}

function compare_outputs() {
	$('button').prop("disabled", true)
	document.getElementById("algs4_output").innerHTML = "";
	var stdjava = extract_code_from_pre("stdjava_code");
	var algs4 = extract_code_from_pre("algs4_code");
	var args = document.getElementById("command_args").value;
	var stdin = document.getElementById("stdin").value;
	show_diff(algs4, stdjava, args, stdin);
}
