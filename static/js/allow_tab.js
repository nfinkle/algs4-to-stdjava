allow_tab = function (e) {
	var keyCode = e.keyCode || e.which;
	if (keyCode === 9) {
		e.preventDefault();

		const TAB_SIZE = 3;

		// The one-liner that does the magic
		document.execCommand('insertText', false, ' '.repeat(TAB_SIZE));
	}
}

$(document).on('keydown', 'textarea', allow_tab);
