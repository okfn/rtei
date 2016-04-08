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
  // add 'subcat' class if an active child input is present onload
  $('.filter input:checked').closest("ul").closest("li").addClass("subcat");

  // add 'subcat' class if a child input is activated
  $('.filter ul ul input').click(function () {
    $(this).closest("ul").closest("li").addClass("subcat");
  });

  // slide non active filter menus up onload
  $( ".filter form > ul > li:not('.subcat') ul" ).slideUp("fast");
  $( ".filter form > ul > li:not('.subcat') h6").removeClass("expanded");

  $( ".filter > ul > li > label" ).click(function() {
    $( ".filter h6" ).removeClass( "expanded" );
    $( ".filter ul.subfilter" ).slideUp();
  });

  $( ".filter h6, .filter label" ).click(function() {
    $( this ).parent().children( "ul" ).slideToggle();
    $( this ).parent().children("h6").toggleClass( "expanded" );
  });

});
