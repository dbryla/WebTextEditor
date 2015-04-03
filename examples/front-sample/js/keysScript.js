

function handleKey(keyCode, body) {
	switch(keyCode) {
		case (8) : {
			if (body.innerHTML ===  "<p><br/></p>") {
				return false;
			} else {
				return true;
			}
		}
	}
}