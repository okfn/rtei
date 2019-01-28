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
        var language = window.location.pathname.match(/^\/[a-zA-Z]{2}\//);
        var path = 'explore/rtei-country?id=' + this.value + '&year=' + RTEI.year;

        path = (language) ? language + path : '/' + path;
        window.location = path;
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

      var value;
      if (chartData[0][this.value] === 0.01 || chartData[0][this.value] === RTEI.insufficientData) {
        value = RTEI.insufficientData;
      } else {
        value = (this.value !== 'index' && this.value.substring(0, 1) != 't') ?
        chartData[0][this.value] * 5 :  // level 1 themes
        chartData[0][this.value];
      }
      $('#current-indicator-value').text(RTEI.formatScore(value));
      RTEI.showIndicators(this.value);
      RTEI.charts.updateChart('country', this.value);
    });


    // indicators
    $("#indicators ul").slideUp().parent().addClass("has-children");
    $('#indicators .indicator').click(function(e){
      $(this).parent().children('ul').not(':animated').slideToggle().parent().toggleClass("open");
    });

});
