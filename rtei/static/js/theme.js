var RTEI = RTEI || {}
RTEI.theme = (function() {


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
    // Sort data by key and rebuild chart.
    var data = RTEI.theme.data;
    if (key != 'name') {
      key = RTEI.theme.currentIndex;
    }
    data = _.sortBy(data, key);
    if (desc) data.reverse();

    RTEI.charts.updateChartConfig('theme', {data: {json: null}});
    RTEI.charts.updateChartConfig('theme', {
      data: {
        json: data
      }
    });
    RTEI.charts.updateChart('theme', RTEI.theme.currentIndex);
    RTEI.theme.currentSort = key;
    RTEI.theme.currentSortDesc = desc;
  };

  function initChart(data, names) {

    // Save a reference for sorting
    RTEI.theme.data = data;

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

    data: null,

    currentIndex: 'index',

    currentSort: 'name',

    init: function(jsonDataFileName) {

      initSortButtons();

      $.getJSON(jsonDataFileName, function(data) {
        var names = $("#chart").data("chart-labels");
        chart = initChart(data, names);
      });
    },

    updateChart: function(code) {
      // Persist the current index for sorting
      // (this will rebuild the chart)
      if (RTEI.theme.currentSort != 'name') {
        sortByKey(RTEI.theme.currentIndex, RTEI.theme.currentSortDesc);
      } else {
        RTEI.charts.updateChart('theme', code);
      }
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
    var label = $('label[for="' + this.id + '"]').text();
    $('#current-indicator-label').text(label);

    if (RTEI.theme.currentIndex != this.value) {
      RTEI.theme.currentIndex = this.value;
    }
    RTEI.theme.updateChart(this.value);
  });

  RTEI.theme.init(jsonDataFileName);
});
