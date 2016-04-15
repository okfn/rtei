var RTEI = RTEI || {}
RTEI.country = (function() {

  var customChartConfig = {
    axis: {
      x: {
          show: false
      },
      y: {
          show: true,
          padding: {
              top: 10,
              bottom: 10
          }
      }
    },
    bar: {
        width: 32
    },
    size: {
      height: 150
    },
    padding: {
      bottom: 10,
      left: 5
    }
  }

  return {

    currentIndex: 'index',

    showIndicators(code) {
      var isTheme = (code.substring(0, 1) == 't');
      if (code != RTEI.country.currentIndex) {
        RTEI.country.currentIndex = code;

        if (!isTheme) {
          if ($('#indicators').is(':hidden')) {
            $('#indicators').show();
          }
          if ($('#theme_indicators').is(':visible')) {
            $('#theme_indicators').hide();
          }

          if (code == 'index') {
            // Show all sections, collapsed
            for (var i = 1; i <= 5; i++) {
              if ($('#indicator_container_' + i).is(':hidden')) {
                $('#indicator_container_' + i).show();
              }
              if ($('#indicator_container_' + i).hasClass('open')) {
                $('#indicator_item_' + i).click();
              }
            }
          } else {
            // Hide other sections
            for (var i = 1; i <= 5; i++) {
              if (String(i) !== code) {
                $('#indicator_container_' + i).hide();
              }
            }
            // Expand relevant section
            if ($('#indicator_container_' + code).is(':hidden')) {
              $('#indicator_container_' + code).show();
            }
            if (!$('#indicator_container_' + code).hasClass('open')) {
              $('#indicator_item_' + code).click();
            }
          }
        } else {
          if ($('#theme_indicators').is(':hidden')) {
            $('#theme_indicators').show();
          }
          if ($('#indicators').is(':visible')) {
            $('#indicators').hide();
          }
          // Show the relevant theme indicators list
          $.each($('.theme-indicators'), function(index, ol) {
            if (ol.id.replace('theme_indicators_', '') != code.replace('t', '')) {
              $(ol).hide();
            } else {
              $(ol).slideDown();
            }
          });
        }
      }
    },


    initChart: function(data, names) {

      RTEI.charts.initChartConfig('country', data, customChartConfig, names);

      RTEI.country.chart = RTEI.charts.updateChart('country', 'index');
    },
  }

})();

$(document).ready(function(){

    // Set up country selector
    $('#available-countries').on('change', function(){
      if (this.value) {
        window.location = '/explore/rtei-country?id=' + this.value;
      }
    });

    // If data available, build the chart
    var chartData = $("#chart").data("chart-data");
    if (chartData) {
      var names = $("#chart").data("chart-labels");
      RTEI.country.initChart(chartData, names);
    }

    // Menu switcher
    $('.indicator-switcher input').on('click', function(){
      var label = $('label[for="' + this.id + '"]').text();
      $('#current-indicator-label').text(label);

      var value = (this.value !== 'index' && this.value.substring(0, 1) != 't') ?
        (chartData[0][this.value] * RTEI.country.chart.groups()[0].length).toFixed(2) :
        chartData[0][this.value];
      $('#current-indicator-value').text(value);
      RTEI.country.showIndicators(this.value);
      RTEI.charts.updateChart('country', this.value);
    });


    // indicators
    $("#indicators ul").slideUp().parent().addClass("has-children");
    $('#indicators .indicator').click(function(e){
      $(this).parent().children('ul').not(':animated').slideToggle().parent().toggleClass("open");
    });

});
