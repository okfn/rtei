var RTEI = RTEI || {}
RTEI.theme = (function() {

  var chart;
  var jsonData;

  var customChartConfig = {
  }

  function initSortButtons() {
    /*
    Initializes the sort buttons.

    The button has either an `asc` or `desc` class that defines its
    current state, which can be used for styling purposes.
    */

    $('#chart-controls :button.sort').each(function(i, el) {
      $(el).on('click', function(ev) {
        var btn = $(ev.target);
        var desc = btn.hasClass('asc');
        $('#chart-controls :button.active').removeClass('active');
        btn.addClass('active');
        if (desc) {
          btn.addClass('desc').removeClass('asc');
        } else {
          btn.addClass('asc').removeClass('desc');
        }
        sortByKey(btn.data('key'), desc);
      });
    });
  };

  function sortByKey(key, desc) {
    // Sort jsonData by key and rebuild chart.
    jsonData = _.sortBy(jsonData, key);
    if (desc) jsonData.reverse();
    chart = buildChart(jsonData);
  };

  function initChart(data, names) {
    // Chart height is the number of rows * 22, or 350, whichever is
    // largest. This ensures there is adequate room for double-lined
    // labels.
    var height = _.max([_.size(data) * 22, 200]);

    customChartConfig.size = {
      height: height
    }

    RTEI.charts.initChartConfig('theme', data, customChartConfig, names);

    RTEI.charts.updateChart('theme', 'index');

  }

  return {

    currentIndex: null,

    init: function(jsonDataFileName) {

      initSortButtons();

      jsonData = $.getJSON(jsonDataFileName, function(data) {

        var names = $("#chart").data("chart-labels");
        chart = initChart(data, names);
      });
    }
  }
})();



$(document).ready(function(){
  // Get the data and initialize the chart.
  // TODO: remove once we have the final data
  var random = Boolean((location.search.split('random=')[1]||'').split('&')[0]);
  var jsonDataFileName = (random) ? 'c3_scores_per_country_random.json': 'c3_scores_per_country.json';
  jsonDataFileName = "/static/data/" + jsonDataFileName;

  // Menu switcher
  $('.indicator-switcher input').on('click', function(){
    /*
    var label = $('label[for="' + this.id + '"]').text();
    $('#current-indicator-label').text(label);

    var value = (this.value !== 'index' && this.value.substring(0, 1) != 't') ?
      (chartData[0][this.value] * RTEI.theme.chart.groups()[0].length).toFixed(2) :
      chartData[0][this.value];
    $('#current-indicator-value').text(value);
    */
    if (RTEI.theme.currentIndex != this.value) {
      RTEI.theme.currentIndex = this.value;
    }
    RTEI.charts.updateChart('theme', this.value);
  });

  RTEI.theme.init(jsonDataFileName);
});
