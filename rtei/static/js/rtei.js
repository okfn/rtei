$(document).ready(function() {
  // JS detection class
  document.documentElement.className = document.documentElement.className.replace("no-js","js");

  // NAV
  $( '#smenu li:has(ul)' ).doubleTapToGo();


  // MAP SWITCHER
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

  $( ".indicator-switcher > ul > li > label" ).click(function() {
    $( ".indicator-switcher h6" ).removeClass( "expanded" );
    $( ".indicator-switcher ul.subindicators" ).slideUp();
  });

  $( ".indicator-switcher h6, .indicator-switcher label" ).click(function() {
    $( this ).parent().children( "ul" ).slideToggle();
    $( this ).parent().children("h6").toggleClass( "expanded" );
  });


  // RESOURCE FILTER
  // parent class
  $('.filter input').click(function () {
    // $("li").removeClass("subcat");
  });

  $('.filter input:checked').closest("ul").closest("li").addClass("subcat");

  $('.filter ul ul input').click(function () {
    $(this).closest("ul").closest("li").addClass("subcat");
  });

  // slide
  $( ".filter h6" ).next( "ul" ).slideUp( "fast");

  $( ".filter > ul > li > label" ).click(function() {
    $( ".filter h6" ).removeClass( "expanded" );
    $( ".filter ul.subfilter" ).slideUp();
  });

  $( ".filter h6, .filter label" ).click(function() {
    $( this ).parent().children( "ul" ).slideToggle();
    $( this ).parent().children("h6").toggleClass( "expanded" );
  });

});
