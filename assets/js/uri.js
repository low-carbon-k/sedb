
var prefixes = new Object();
prefixes["se"] = "http://www.teitanso.org/2012/04/se#";

function arrangePrefix(data) {
	$.each(prefixes, function(key, value) {
		data = data.replace(value, key + ":");
	})
	return data;
}

function rearrangePrefix(data) {
	var str = data.split(":");
	// console.log(str);
	return prefixes[str[0]] + str[1];
}

function getPrefixes() {
	var prefix = "";
	$.each(prefixes, function(key, value) {
		prefix += " PREFIX " + key + ": <" + value + ">  ";
	});
	return prefix;
}
