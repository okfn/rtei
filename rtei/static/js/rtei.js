$(document).ready(function() {
  //nav
  $( '#smenu li:has(ul)' ).doubleTapToGo();


  //map switcher
  $('.indicator-switcher input').click(function () {
    $("li").removeClass("subcat");
  });

  $('.indicator-switcher input:checked').closest("ul").closest("li").addClass("subcat");

  $('.indicator-switcher ul ul input').click(function () {
    $(this).closest("ul").closest("li").addClass("subcat");
  });
});
