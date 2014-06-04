jQuery(function($){
               $(".date").mask("99/99/9999");
            });

$(function() {
    $( ".date_picker" ).datepicker({
         changeMonth: true,
         changeYear: true
    });
});