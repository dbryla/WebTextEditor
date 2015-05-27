/**
 *	Helper functions for String operations.
 */

/**
 *	Inserts specified string inside String object on specified index.
 */
String.prototype.insert = function (index, string) {
	if (index > 0) {
		return this.substring(0, index) + string + this.substring(index, this.length);
	}
	else {
		return string + this;
	}
};


/**
 *	Returns index of first difference between string s and String object the function is called on.
 */
String.prototype.indexOfFirstDifference = function(s, caseInsensitive){
	var l = this.length, i = -1;
	while( ++i < l){
		if ( !s[i]) {
			return i;
		}
		var diff = caseInsensitive ? this[i].toUpperCase() !== s[i].toUpperCase() : this[i] !== s[i];
		if ( diff ) {  
			return i; 
		}
	}
	return s.length > l ? l : null;
};