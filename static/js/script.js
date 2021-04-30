 $(document).ready(function () {
     $('.sidenav').sidenav({
         edge: "right"
     });
     $('.collapsible').collapsible();
     $('#textarea1').val('');
     M.textareaAutoResize($('#textarea1'));
 });