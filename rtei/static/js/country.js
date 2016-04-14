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

    baseChartConfig: {
      bindto: '#chart',
      data: {
        json: null,
        order: null,
        /*
         * You'll need to set up the following on each refresh:
         *
        keys: {
            x: 'name',
            value: ['1', '3', '2', '5', '4']
        },
        groups: [
            ['1', '2', '3', '4', '5']
        ],
        */

        colors: {
          1: '#c35727',
          2: '#bdb831',
          3: '#af1f2c',
          4: '#357b9e',
          5: '#469a8f',
        },
        type: 'bar'
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
          width: 32
      },
      tooltip: {
        format: {
          value: function (value, ratio, id, index) {
            if (RTEI.country.chart.groups().length) {
              return parseFloat((value * RTEI.country.chart.groups()[0].length).toFixed(2));
            } else {
              return value;
            }
          }
        }
      },
      size: {
        height: 150
      },
      padding: {
        bottom: 10,
        left: 5
      },
      transition: {
        duration: 300
      }
    },

    initChart: function(jsonData, names) {

      var config = RTEI.country.baseChartConfig;
      if (!config.data.json) {
        config.data.json= jsonData;
      }
      config.data.names = names;

      var colors = {};
      var indicator, subIndicator;
      for (var key in names) {
        if (names.hasOwnProperty(key)) {
          if (key.substring(0, 1) == 't') {
            // Theme, use the default
            colors[key] = RTEI.colors.index[0];
          } else if (key.indexOf('.') !== -1) {
            // Indicator level 2
            indicator = key.split('.')[0];
            subIndicator = key.split('.')[1];
            colors[key] = RTEI.colors[indicator][parseInt(subIndicator) - 1];
          } else {
            //Indicator level 1
            colors[key] = RTEI.colors[key][0];
          }
        }
      }
      config.data.colors = colors;

      RTEI.country.updateChart('index');
    },

    updateChart: function(code) {
      var chart = RTEI.country.chart;
      var config = RTEI.country.baseChartConfig;
      var values = [];

      if (chart) {
        chart = chart.destroy;
      }

      if (code == 'index') {
        values = ['1', '2', '3', '4', '5'];
      } else if (code.substring(0, 1) != 't') {
        for (var key in config.data.names) {
          if (config.data.names.hasOwnProperty(key) &&
              key.substring(0, 1) == code &&
              key.indexOf('.') !== -1) {
            values.push(key);
          }
        }
      } else {
        values = [code]
      }

      var customConfig = $.extend(true, {}, config, {
        data: {
          keys : {
            x: 'name',
            value: values
          },
          groups: [
            values
          ]
        }
      });
      RTEI.country.chart = c3.generate(customConfig);
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
      RTEI.country.updateChart(this.value);
    });


    // indicators
    $("#indicators ul").slideUp().parent().addClass("has-children");
    $('#indicators .indicator').click(function(e){
      $(this).parent().children('ul').not(':animated').slideToggle().parent().toggleClass("open");
    });

});
