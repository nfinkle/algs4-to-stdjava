function compile() {
	var code = document.getElementById("code_form").elements[0].value;
	// var cur_inner = document.getElementById("stdjava_code").elements[0].value;
	// var tmp = cur_inner.replace(/\s\s/g, "").split(">");
	// var code;
	// for (i = 0; i < tmp.length; i++) {
	// 	if (tmp[i].includes("font-size")) {
	// 		code = tmp[i + 1];
	// 		code = code.replace(/<.*/, "");
	// 		break;
	// 	}
	// }
	document.getElementById("stdjava_code").innerHTML = "<pre class=\"line-numbers\" style=\"white-space:pre-wrap; font-size:11px\"><code class=\"language-java match-braces\">" + code.replace(/</g, "&lt").replace(/>/g, "&gt") + "</code></pre>" + "<button type=\"button\" class=\"btn btn-primary\" onclick=\"edit()\">Edit</button>";
	Prism.highlightAll();
}

function getString(arr, start, n) {
	newString = ""
	for (i = 0; i < n; i++) {
		newString += arr[i + start];
	}
	return newString;
}

function edit() {
	var cur_inner = document.getElementById("stdjava_code").innerHTML;
	var tmp = cur_inner /*.replace(/\s\s/g, "")*/ .replace(/<button.*/, "");
	var i = 0;
	var code = "";
	for (i = 0; i < tmp.length; i++) {
		var five = getString(tmp, i, 5);
		var six = five + tmp[i + 5];
		if (five == "<span" || six == "</span" || getString(tmp, i, 4) == "<pre" || five == "<code" || five == "</pre" || six == "</code") {
			for (; i < tmp.length && tmp[i] != ">"; i++);
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
	var lines = (code.match(/\n/g) || []).length
	document.getElementById("stdjava_code").innerHTML = "<form id=\"code_form\" spellcheck=\"false\"><p><textarea style=\"font-size: 11px\"; rows=\"" + lines + "\";>" + code + "</textarea></p></form>" + "<button type=\"button\" class=\"btn btn-primary\" onclick=\"compile()\">Compile</button>";
	">"
}

function execute() {
	xhttp.open("GET", "/run_code", true);
}
