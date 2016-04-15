var RTEI = RTEI || {}
RTEI.theme = (function() {

    var chart;
    var jsonData;

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

    function buildChart(data) {
        // Chart height is the number of rows * 22, or 350, whichever is
        // largest. This ensures there is adequate room for double-lined
        // labels.
        var height = _.max([_.size(data) * 22, 200]);
        var chart = c3.generate({
            bindto: '#chart',
            data: {
                json: data,
                order: null,
                keys: {
                    x: 'name',
                    value: ['1', '3', '2', '5', '4'],
                },
                groups: [
                    ['1', '2', '3', '4', '5'],
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
                    type: 'category'
                },
                y: {
                    show: true,
                    max: 100,
                    padding: {
                        top: 10,
                    }
                }
            },
            bar: {
                width: 16
            },
            size: {
                height: height
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
            }
        });
        return chart;
    };

    return {
        init: function(jsonDataFileName) {

            initSortButtons();

            jsonData = $.getJSON(jsonDataFileName, function(data) {
                jsonData = data;
                chart = buildChart(jsonData);
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

    RTEI.theme.init(jsonDataFileName);
});
