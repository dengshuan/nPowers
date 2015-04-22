$(document).ready(function() {
    $("#add").click(function() {
	$("#from option:selected").each(function() {
	    $(".hide select option[value=" + $(this).val() +"]").prop("selected", true);
	    $(this).remove().appendTo("#to");
	});
    });
    $("#remove").click(function() {
	$("#to option:selected").each(function() {
	    $(".hide select option[value=" + $(this).val() +"]").prop("selected", false);
	    $(this).remove().appendTo("#from");
	});
    });
});
