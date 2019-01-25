var RTEI = RTEI || {}
RTEI.charts = (function() {

  var baseChartConfig = {
    bindto: '#chart',
    data: {
      json: null,
      order: null,
      type: 'bar'
    },
    axis: {
      rotated: true,
      x: {
          type: 'category',
          show: true,
          tick: {
            multiline: false
          }
      },
      y: {
          show: true,
          max: 100,
          padding: {
              top: 10
          }
      }
    },
    bar: {
        width: 16
    },
    tooltip: {
      format: {
        value: function (value, ratio, id, index) {
          if (value === 0.01) {
            return RTEI.insufficientData;
          }
          if (id.substring(0, 1) != 't') {
            if (id.indexOf('.') === -1) {
              if (id == 'O' || id == 'P' || id == 'S') {
                return RTEI.formatScore(value)
              } else {
                return RTEI.formatScore(value * RTEI.charts.categoriesLength.index);
              }
            } else {
              var key = id.split('.')[0];
              return RTEI.formatScore(value * RTEI.charts.categoriesLength[key]);
            }
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
      bottom: 20
    },
    transition: {
      duration: 300
    }
  }

  var register = {};

  return {

    categoriesLength: {},

    initChartConfig: function(chartId, data, customChartConfig, names) {

      var config = $.extend(true, {}, baseChartConfig, customChartConfig);
      if (!config.data.json) {
        config.data.json= data;
      }

      if (names) {
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

              if (RTEI.charts.categoriesLength[indicator]) {
                RTEI.charts.categoriesLength[indicator]++;
              } else {
                RTEI.charts.categoriesLength[indicator] = 1;
              }
            } else {
              //Indicator level 1
              colors[key] = RTEI.colors[key][0];
              if (RTEI.charts.categoriesLength['index']) {
                RTEI.charts.categoriesLength['index']++;
              } else {
                RTEI.charts.categoriesLength['index'] = 1;
              }
            }
          }
        }
        config.data.colors = colors;
      }

      register[chartId] = {};
      register[chartId].config = config;

      return config;
    },

    updateChartConfig: function(chartId, customConfig) {
      var config = register[chartId].config;
      $.extend(true, config, customConfig);

      return config;
    },

    updateChart: function(chartId, code) {
      var config = register[chartId].config;
      var chart = register[chartId].chart;

      if (chart) {
        chart = chart.destroy;
      }

      var values = [];
      if (code == 'index') {
        values = ['S', 'P', 'O'];
      } else if (code.substring(0, 1) != 't') {
        noData = [];
        for (var i = 0; i < config.data.json.length; i++) {
          country = config.data.json[i];

          if (country[code] == RTEI.insufficientData || country[code] == 0.01) {
            // All theme (1,2,3,4) has insufficient data
            noData.push(country['name']);

            for (var key in config.data.names) {
              if (key.substring(0, 1) == code) {
                country[key] = 0.01;
              }
            }
          } else {
            for (var key in config.data.names) {
              if (key.substring(0, 1) == code) {
                if (country[key] == RTEI.insufficientData) {
                  country[key] = 0.01;
                }
              }
            }
          }
        }
        if (noData.length == config.data.json.length) {
          // No data available for all countries, don't build the graph
          config.tooltip.show = false;
          $('#chart-insufficient-data').show();
        } else {
          config.tooltip.show = true;
          $('#chart-insufficient-data').hide();
        }

        for (var key in config.data.names) {
          if (config.data.names.hasOwnProperty(key) &&
              key.substring(0, 1) == code &&
              key.indexOf('.') !== -1) {
            values.push(key);
          }
        }
      } else {
        values = [code]
        config.tooltip.show = true;
        $('#chart-insufficient-data').hide();
       }
      values.sort()

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

      register[chartId].chart = c3.generate(customConfig);
      return register[chartId].chart
    }
  }

})();
