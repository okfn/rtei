var RTEI = RTEI || {};


$(document).ready(function() {

  RTEI.colors = {
    index: ['#4598c2', '#73b2d1', '#96c5dc', '#b8d8e8', '#dbebf3'],
    1: ['#c35727', '#db784c', '#e39572', '#ebb299', '#f2cfbf'],  // governance
    2: ['#bdb831', '#d4cf58', '#ddda7c', '#e7e4a1', '#f0eec5'],  // availability
    3: ['#af1f2c', '#da3140', '#e15864', '#e87f88', '#efa6ac'],  // accessibility
    4: ['#357b9e', '#4d9cc3', '#6fafcf', '#92c2da', '#b4d5e6'],  // acceptability
    5: ['#469a8f', '#64b9ae', '#84c7be', '#a4d5cf', '#c3e4e0']  // adaptability
  };

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

  $('.indicator-switcher input').on('click', function(){
    var isTheme = (this.value.substring(0, 1) == 't');
    var label = $('label[for="' + this.id + '"]').text();

    if (isTheme) {
      className = 'overall_index';
    } else if (this.id.indexOf('.') !== -1) {
      className = $('label[for="' + this.id.substring(0, this.id.indexOf('.')) + '"]').text();
    } else {
      className = label;
    }
    var templateClassNames = [];
    $.each($('body').attr('class').split(/\s+/), function(index, item) {
        if (item && item.substring(0, 8) == 'template') {
            templateClassNames.push(item);
        }
    });
    $('body').attr('class', templateClassNames.join(' ') + ' ' + className.toLowerCase().replace(' ', '_'));
  });

  // slide
  $( ".indicator-switcher h6" ).next( "ul" ).slideUp( "fast");

  $( ".indicator-switcher > ul > li > label" ).click(function() {
    $( ".indicator-switcher h6" ).removeClass( "expanded" );
    $( ".indicator-switcher ul.subindicators" ).slideUp();
  });

  $( ".indicator-switcher h6, .indicator-switcher label" ).click(function() {
    var $this = $(this);
    $this.parent().children( "ul" ).slideToggle();
    $this.parent().children("h6").toggleClass( "expanded" );
    var code = $this.attr('for').replace('indicator_', '');
    var isTheme = (code.substring(0, 1) == 't');
    if (isTheme) {
      if (code.slice(-1).search(/[A-Za-z\s]/) === -1) {
        // First level Tranversal Theme, we want to select the first child
        // by default
        $this.parent().children('ul.subindicators').children('li').first().children('input').click();
        return false;
      }
    }

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
