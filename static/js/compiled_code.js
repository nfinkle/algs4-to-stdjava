function compile_sm() {
	var code = document.getElementById("code_form_sm").elements[0].value;
	compile_with_code(code);
}

function compile() {
	var code = document.getElementById("code_form").elements[0].value;
	compile_with_code(code);
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

function compile_with_code(code) {
	$('button').prop("disabled", true)
	document.getElementById("algs4_output").innerHTML = "";
	$.ajax({
		url: "/compile_code",
		async: true,
		cache: false,
		data: {
			"code": code,
			"is_algs4": false,
		},
		success: function (result) {
			add_execute_button = display_compile_error(result)
			replaceFormWithPre(code, add_execute_button);
			Prism.highlightAll();
			$('button').prop("disabled", false)
		}
	})
}


function replaceFormWithPre(code, add_execute_button) {
	var new_html = "<pre class=\"line-numbers\" style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-java match-braces\">" + code.replace(/</g, "&lt").replace(/>/g, "&gt") + "</code></pre>" + "<button type=\"button\" class=\"btn btn-primary\" id=\"edit_btn\" onclick=\"edit()\">Edit</button>";
	if (add_execute_button) {
		new_html += "<button type = \"button\" class=\"btn btn-primary\" id=\"execute_btn\" onclick=execute()>Execute</button>";
		tests = $('#tests-data').data().other
		new_html += '<button type="button" class="btn btn-primary" onclick="compare_outputs()">Compare</button>'
		new_html += '<button type="button" class="btn btn-primary" onclick="run_tests(' + tests + ')">Run Tests</button>'
	}
	document.getElementById("stdjava_code").innerHTML = new_html;
	document.getElementById("stdjava_code_sm").innerHTML = new_html;
}

function getString(arr, start, n) {
	newString = ""
	for (i = 0; i < n; i++) {
		newString += arr[i + start];
	}
	return newString;
}

function extract_code_from_pre(id) {
	var cur_inner = document.getElementById(id).innerHTML;
	var tmp = cur_inner /*.replace(/\s\s/g, "")*/ .replace(/<button.*/, "");
	var code = "";
	for (var i = 0; i < tmp.length; i++) {
		var five = getString(tmp, i, 5);
		var six = five + tmp[i + 5];
		if (five == "<span" || six == "</span" || getString(tmp, i, 4) == "<pre" || five == "<code" || five == "</pre" || six == "</code") {
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

	return code;
}

function edit() {
	$('button').prop("disabled", true)
	var code = extract_code_from_pre("stdjava_code");
	var lines = (code.match(/\n/g) || []).length
	var new_html_start = "<form id=\"code_form_version\" spellcheck=\"false\"><p><textarea id=\"form_textarea_version\" style=\"font-size: 11px\"; rows=\"";
	var middle = lines + "\";>" + code
	var new_html_end = "</textarea>" + "<button type=\"button\" class=\"btn btn-primary\" onclick=\"compile_version()\">Compile</button></p></form>";
	var new_html_default = new_html_start.replace(/_version/g, "") + middle + new_html_end.replace(/_version/g, "");
	var new_html_sm = new_html_start.replace(/_version/g, "_sm") + middle + new_html_end.replace(/_version/g, "_sm")
	document.getElementById("stdjava_code").innerHTML = new_html_default;
	document.getElementById("stdjava_code_sm").innerHTML = new_html_sm;
	$('button').prop("disabled", false)
}

function execute_from_code(code, is_algs4, command_args, stdin) {
	ret_fn = function (result) {
		$('button').prop("disabled", false);
		html = ""
		if (result[0]) {
			const pre_output_html = "<h4>Output</h4><pre  style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-markdown match-braces\">";
			const post_output_html = "</code></pre>";
			html += pre_output_html + result[0] + post_output_html;
		}
		if (result[1]) {
			const pre_err_html = "<h4>Error</h4><pre style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-javastacktrace match-braces\">";
			const post_err_html = "</code></pre>";
			html += pre_err_html + result[1] + post_err_html;
		}

		document.getElementById("algs4_output").innerHTML = html;
		Prism.highlightAll();
	}
	send_exec_request(code, is_algs4, command_args, stdin, ret_fn)
}

function execute_algs4() {
	$('button').prop("disabled", true)
	document.getElementById("algs4_output").innerHTML = "";
	var code = extract_code_from_pre("algs4_code").replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	var args = document.getElementById("command_args").value;
	var stdin = document.getElementById("stdin").value;
	execute_from_code(code, true, args, stdin);
}

function execute() {
	$('button').prop("disabled", true)
	document.getElementById("algs4_output").innerHTML = "";
	var code = extract_code_from_pre("stdjava_code").replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	var args = document.getElementById("command_args").value;
	var stdin = document.getElementById("stdin").value;
	execute_from_code(code, false, args, stdin);
}

function send_exec_request(code, is_algs4, command_args, stdin, ret_fn) {
	$.ajax({
		url: "/run_code",
		async: true,
		cache: false,
		data: {
			"code": code,
			"is_algs4": is_algs4,
			"args": command_args,
			"stdin": stdin
		},
		success: function (result) {
			ret_fn(result)
		}
	})
}

function run_next_test(ith_test, result, code, test_list) {
	// alert("finished test " + ith_test)
	cur_html = document.getElementById("algs4_output").innerHTML.replace(/&gt;/g, ">").replace(/&lt;/g, "<")
	cur_html = cur_html.split("Running")[0]; // replace Running and pre closes
	cur_html += "Test " + ith_test + ": "
	const desired_output = test_list[ith_test]["out"]
	if (result[0].valueOf() === desired_output[0].valueOf() && result[1].valueOf() === desired_output[1].valueOf()) {
		cur_html += "Success!\n"
	} else if (result[0].valueOf() === desired_output[0].valueOf()) {
		cur_html += "Correct output, but not error.\n"
	} else if (result[1].valueOf() === desired_output[1].valueOf() && (result[1] || desired_output[1])) {
		cur_html += "Correct error, but not output.\n"
	} else {
		cur_html += "Failed.\n"
	}
	if (ith_test < test_list.length - 1) {
		cur_html += "Running Test " + (ith_test + 1) + "\n";
		send_exec_request(code, false, test_list[ith_test + 1]["arg"], test_list[ith_test + 1]["stdin"], function (result) {
			run_next_test(ith_test + 1, result, code, test_list)
		})
	} else {
		$('button').prop("disabled", false);
	}
	cur_html += "</code></pre>"
	document.getElementById("algs4_output").innerHTML = cur_html
	Prism.highlightAll();
}

function run_tests(test_list) {
	$('button').prop("disabled", true);
	var code = extract_code_from_pre("stdjava_code").replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	document.getElementById("algs4_output").innerHTML = "<h4>Tests</h4><pre style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-java\">Running Test 0\n</code></pre>";
	Prism.highlightAll();
	send_exec_request(code, false, test_list[0]["arg"], test_list[0]["stdin"], function (result) {
		run_next_test(0, result, code, test_list);
	})
}



function show_diff(algs4_result, stdjava_result) {
	$.ajax({
		url: "/get_diff",
		async: true,
		cache: false,
		data: {
			"algs4_out": algs4_result[0],
			"stdjava_out": stdjava_result[0],
			"algs4_err": algs4_result[1],
			"stdjava_err": stdjava_result[1]
		},
		success: function (result) {
			// alert(result)
			html = ""
			if (result[0]) {
				const pre_out_html = "<h4>Outputs</h4><pre style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-diff\">";
				const post_out_html = "</code></pre>";
				html += pre_out_html + result[0] + post_out_html;
			}
			if (result[1]) {
				const pre_err_html = "<h4>Errors</h4><pre style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-diff\">";
				const post_err_html = "</code></pre>";
				html += pre_err_html + result[1] + post_err_html;
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
	var stdjava = extract_code_from_pre("stdjava_code").replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	var algs4 = extract_code_from_pre("algs4_code").replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	var args = document.getElementById("command_args").value;
	var stdin = document.getElementById("stdin").value;
	ret_fn = function (algs4_result) {
		send_exec_request(stdjava, false, args, stdin, function (snd) {
			show_diff(algs4_result, snd)
		})
	}
	send_exec_request(algs4, true, args, stdin, ret_fn)

}
