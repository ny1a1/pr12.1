(function(input) {
    var value = parseFloat(input);
    return JSON.stringify({
        "device": "sensor1",
        "value": value,
        "unit": "C"
    });
})(input)