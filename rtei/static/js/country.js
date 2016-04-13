var RTEI = RTEI || {}
RTEI.country = (function() {

  return {

    currentIndex: null,

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

    initChart: function(data) {
      var chart;
      var json_data;
      var chart = c3.generate({
          bindto: '#chart',
          data: {
              json: data,
              order: null,
              keys: {
                  x: 'name',
                  value: ['1', '3', '2', '5', '4']
              },
              groups: [
                  ['1', '2', '3', '4', '5']
              ],
              names: {
                  '1': 'Governance',
                  '3': 'Accessibility',
                  '2': 'Availability',
                  '5': 'Adaptability',
                  '4': 'Acceptability'
              },
              type: 'bar',
              colors: {
                1: '#c35727',
                2: '#bdb831',
                3: '#af1f2c',
                4: '#357b9e',
                5: '#469a8f',
              },
          },
          axis: {
              rotated: true,
              x: {
                  type: 'category',
                  show: false,
              },
              y: {
                  show: true,
                  max: 100,
                  padding: {
                      top: 10,
                      bottom: 10,
                  }
              }
          },
          bar: {
              width: 16
          },
          tooltip: {
            format: {
              value: function (value, ratio, id, index) {
                  return parseFloat((value * 5).toFixed(2));
              }
            }
          },
          padding: {
            bottom: 20,
            left: 5
          }
      });
    }
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
      RTEI.country.initChart(chartData);
    }

    // Menu switcher
    $('.indicator-switcher input').on('click', function(){
      RTEI.country.showIndicators(this.value);
    });


    // indicators
    $("#indicators ul").slideUp().parent().addClass("has-children");
    $('#indicators .indicator').click(function(e){
      $(this).parent().children('ul').not(':animated').slideToggle().parent().toggleClass("open");
    });

});
