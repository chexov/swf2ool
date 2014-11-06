var SimpleAjax = function(){
}

SimpleAjax.prototype.load = function (url, callback, error) {
    var http = new XMLHttpRequest();
    http.open("GET", url, true);
    http.onreadystatechange = function () {
        if (http.readyState == 4) {
            if (http.status == 200) {
                var result = "";
                if (http.responseText)
                    result = http.responseText;
                if (callback)
                    callback(result);
            } else {
                if (console)
                    console.log(http.status);
                if (error) {
                    error(http);
                }
            }
        }
    };
    http.send(null);
    return http;
};

SimpleAjax.prototype.loadJson = function (url, callback, error) {
    return this.load(url, function (result, httpStatus) {
        if (callback) {
            var resultObj = result;
            if (result) {
                resultObj = JSON.parse ? JSON.parse(result) : JSON.decode(result)
            }
            ;
            callback(resultObj, httpStatus);
        }
        ;
    }, error);
};

