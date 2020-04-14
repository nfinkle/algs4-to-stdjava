function compile_sm() {
	$('button').prop("disabled", true)
	var code = document.getElementById("code_form_sm").elements[0].value;
	compile_with_code(code);
}

function compile() {
	$('button').prop("disabled", true)
	var code = document.getElementById("code_form").elements[0].value;
	compile_with_code(code);
}

// This function displays the compiler error, but does not render the Prism output
function display_compile_error(compile_err) {
	var err_html = "";
	if (compile_err) {
		console.log(compile_err);
		const pre_err_html = "<h4>  Compile Error</h4><pre class=\"line-numbers\" style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-javastacktrace match-braces\">";
		const post_err_html = "</code></pre>";
		err_html = pre_err_html + compile_err + post_err_html;
	}
	document.getElementById("algs4_output").innerHTML = err_html;
	return !compile_err;
}

function compile_with_code(code) {
	$.ajax({
		url: "/compile_code",
		async: true,
		data: {
			"code": code,
			"is_algs4": true
		},
		success: function (result) {
			// console.log("hi")
			add_execute_button = display_compile_error(result)
			replaceFormWithPre(code, add_execute_button);
			Prism.highlightAll();
		}
	})
}


function replaceFormWithPre(code, add_execute_button) {
	var new_html = "<pre class=\"line-numbers\" style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-java match-braces\">" + code.replace(/</g, "&lt").replace(/>/g, "&gt") + "</code></pre>" + "<button type=\"button\" class=\"btn btn-primary\" id=\"edit_btn\" onclick=\"edit()\">Edit</button>";
	if (add_execute_button) {
		new_html += "<button type = \"button\" class=\"btn btn-primary\" id=\"execute_btn\" onclick=\"execute()\">Execute</button>";
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

function extract_code_from_pre() {
	var cur_inner = document.getElementById("stdjava_code").innerHTML;
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
	var code = extract_code_from_pre();
	var lines = (code.match(/\n/g) || []).length
	var new_html_start = "<form id=\"code_form_version\" spellcheck=\"false\"><p><textarea id=\"form_textarea_version\" style=\"font-size: 11px\"; rows=\"";
	var middle = lines + "\";>" + code
	var new_html_end = "</textarea>" + "<button type=\"button\" class=\"btn btn-primary\" onclick=\"compile_version()\">Compile</button></p></form>";
	var new_html_default = new_html_start.replace(/_version/g, "") + middle + new_html_end.replace(/_version/g, "");
	var new_html_sm = new_html_start.replace(/_version/g, "_sm") + middle + new_html_end.replace(/_version/g, "_sm")
	document.getElementById("stdjava_code").innerHTML = new_html_default;
	document.getElementById("stdjava_code_sm").innerHTML = new_html_sm;
}


function execute() {
	$('button').prop("disabled", true)
	$('#execute_btn').prop("disabled", true)
	$('#edit_btn').prop("disabled", true)
	console.log("Beginning execution")
	var code = extract_code_from_pre().replace(/&gt;/g, ">").replace(/&lt;/g, "<");
	console.log(code);
	$.ajax({
		url: "/run_code",
		async: true,
		data: {
			"code": code,
			"is_algs4": true
		},
		success: function (result) {
			$('button').prop("disabled", false)
			console.log(result);
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
	})
}
