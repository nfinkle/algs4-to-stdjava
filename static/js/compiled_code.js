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
	$.ajax({
		url: "/compile_code",
		async: true,
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
	}
	new_html += '<button type="button" class="btn btn-primary" onclick="compare_outputs()">Compare</button>'
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

function execute_from_code(code, is_algs4, command_args) {
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
	send_exec_request(code, is_algs4, command_args, ret_fn)
}

function execute_algs4() {
	$('button').prop("disabled", true)
	var code = extract_code_from_pre("algs4_code").replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	var args = document.getElementById("command_args").innerHTML;
	execute_from_code(code, true, args);
}

function execute() {
	$('button').prop("disabled", true)
	var code = extract_code_from_pre("stdjava_code").replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	var args = document.getElementById("command_args").innerHTML;
	execute_from_code(code, false, args);
}

function send_exec_request(code, is_algs4, command_args, ret_fn) {
	$.ajax({
		url: "/run_code",
		async: true,
		data: {
			"code": code,
			"is_algs4": is_algs4,
			"args": command_args
		},
		success: function (result) {
			ret_fn(result)
		}
	})
}

function show_diff(algs4_result, stdjava_result) {
	$.ajax({
		url: "/get_diff",
		async: true,
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
	var stdjava = extract_code_from_pre("stdjava_code").replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	var algs4 = extract_code_from_pre("algs4_code").replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	var args = document.getElementById("command_args").innerHTML;
	ret_fn = function (algs4_result) {
		send_exec_request(stdjava, false, args, function (snd) {
			show_diff(algs4_result, snd)
		})
	}
	send_exec_request(algs4, true, args, ret_fn)

}
