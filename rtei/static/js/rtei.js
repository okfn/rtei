$(document).ready(function() {
  // nav
  $( '#smenu li:has(ul)' ).doubleTapToGo();


  // map switcher
  // parent class
  $('.indicator-switcher input').click(function () {
    $("li").removeClass("subcat");
  });

  $('.indicator-switcher input:checked').closest("ul").closest("li").addClass("subcat");

  $('.indicator-switcher ul ul input').click(function () {
    $(this).closest("ul").closest("li").addClass("subcat");
  });

  // slide
  $( ".indicator-switcher h6" ).next( "ul" ).slideUp( "fast");
  $( ".indicator-switcher h6" ).click(function() {
    $( this ).next( "ul" ).slideToggle();
    $( this ).toggleClass( "expanded" );
  });

});
