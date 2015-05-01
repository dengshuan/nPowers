$(document).ready(function() {
    $("#upload-file").change(function(event) {
	$("#uploading").show();
    });

    $("#upload").click(function() {
	var fd = new FormData($("#upload-form")[0]);
	$.ajax({
	    xhr: function() {
		var xhr = new window.XMLHttpRequest();
		xhr.upload.addEventListener("progress", function(event) {
		    if(event.lengthComputable) {
			var percentComplete = event.loaded / event.total;
			$("#progressbar").css("width", Math.round(100*percentComplete) + "%");
		    }
		}, false);
		return xhr;
	    },
	    url: "http://upload.qiniu.com",
	    type: "post",
	    data: fd,
	    enctype: "multipart/form-data",
	    processData: false,
	    contentType: false
	}).done(function(data) {
	    $("#thumbnail")[0].src = data.url;
	    $("#thumbnail").show();
	    $("#img").val(data.uuid);
	});
	return false;
    });
});
