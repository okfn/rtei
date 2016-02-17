var RTEI = RTEI || {}
RTEI.country = (function() {

  return {
    initChart: function(data){
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
                1: '#ffb21a',
                2: '#4ccd55',
                3: '#39abe0',
                4: '#7d5fba',
                5: '#c6539b',
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

});
