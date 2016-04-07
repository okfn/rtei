var RTEI = RTEI || {}
RTEI.map = (function() {

  var homepage = window.location.href.indexOf('explore/map') === -1;

  var colors = {
    index: ['#4598c2', '#73b2d1', '#96c5dc', '#b8d8e8', '#dbebf3'],
    1: ['#c35727', '#db784c', '#e39572', '#ebb299', '#f2cfbf'],  // governance
    2: ['#bdb831', '#d4cf58', '#ddda7c', '#e7e4a1', '#f0eec5'],  // availability
    3: ['#af1f2c', '#da3140', '#e15864', '#e87f88', '#efa6ac'],  // accessibility
    4: ['#357b9e', '#4d9cc3', '#6fafcf', '#92c2da', '#b4d5e6'],  // acceptability
    5: ['#469a8f', '#64b9ae', '#84c7be', '#a4d5cf', '#c3e4e0']  // adaptability
  };

  // get color depending on the selected index
  function getColor(score) {
    if (!score) {
      if (homepage) {
        return 'rgba(255,255,255,0.4)';
      } else {
        return '#bebebd';
      }
    }
    score = parseFloat(score);

    var palette = (RTEI.map.currentIndex.indexOf('.') !== -1) ?
      colors[RTEI.map.currentIndex.substring(0, RTEI.map.currentIndex.indexOf('.'))] :
      colors[RTEI.map.currentIndex];
    return score > 80 ? palette[0] :
           score > 60 ? palette[1] :
           score > 40 ? palette[2] :
           score > 20 ? palette[3] :
           score > 0  ? palette[4] :
                    '#bebebd';
  }

  function style(feature) {

    if (homepage) {
      bColour = '#333';
    } else {
      bColour = '#fff';
    }

    return {
      weight: 1,
      opacity: 1,
      color: bColour,
      fillOpacity: 1,
      fillColor: getColor(feature.properties[RTEI.map.currentIndex])
    };
  }

  function highlightFeature(e) {

    if (homepage) {
      hlColour = '#fff';
    } else {
      hlColour = '#666';
    }

    var layer = e.target;
    layer.setStyle({
      weight: 2,
      color: hlColour,
      dashArray: '',
    });

    if (!L.Browser.ie && !L.Browser.opera) {
      layer.bringToFront();
    }
  }

  var geoJSONLayer;

  function resetHighlight(e) {
    geoJSONLayer.resetStyle(e.target);
  }

  function zoomToFeature(e) {
    RTEI.map.map.fitBounds(e.target.getBounds());
  }

  function popupContent(feature) {
    var content = ''
    content += '<div class="popup-content">';

    if (RTEI.map.currentIndex != 'index' &&
        feature.properties[RTEI.map.currentIndex]) {
      content += ' <div class="country-score"><span>' + RTEI.map.currentIndexLabel + ': </span>' + feature.properties[RTEI.map.currentIndex] + '</div>';
    } else if (feature.properties.index) {
      content += ' <div class="country-score"><span>Overall Index: </span>' + feature.properties.index + '</div>';
    }
    if (feature.properties.index) {
      content += ' <div class="country-name has-properties">' + feature.properties.name + '</div>';
      content += ' <div class="more-details"><a href="/explore/rtei-country/?id=' + feature.properties.iso2 + '">Full country scores</a></div>';
    } else {
      content += ' <div class="no country-score">No data available</div>';
      content += ' <div class="country-name">' + feature.properties.name + '</div>';
    }
    return content;
  }

  function onEachFeature(feature, layer) {

    layer.bindPopup(popupContent(feature), {
      className: 'rtei-map-popup'}
    );
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight
    });
  }

  var customGeoJSONLayer = L.geoJson(null, {
      style: style,
      onEachFeature: onEachFeature
  });


  return {

    // The actual Leaflet map object
    map: null,

    // The index to display ('index' for the overall score, '1', '1.1', etc otherwise)
    currentIndex: 'index',

    // The label for index to display (Not used for the overall score, 'Governance',
    // 'International law', etc otherwise)
    currentIndexLabel: null,

    init: function() {
      if (homepage) {
        RTEI.map.map = L.map('map', {
          attributionControl: false,
          zoomControl: false
        }).setView([43, 15], 1.60);
        L.control.zoom({position: 'topright'}).addTo(RTEI.map.map);

      } else {
        RTEI.map.map = L.map('map', {
          attributionControl: false,
          zoomControl: false
        }).setView([40, 10], 1.5);
        L.control.zoom({position: 'topright'}).addTo(RTEI.map.map);
      }

      // TODO: remove once we have the final data
      var random = Boolean((location.search.split('random=')[1]||'').split('&')[0]);
      var fileName = (random) ? 'countries_random.topojson': 'countries.topojson';
      geoJSONLayer = omnivore.topojson('/static/data/' + fileName, null , customGeoJSONLayer)
        .addTo(RTEI.map.map);

    },

    // Refresh the countries layer symbology depending on the current index
    refresh() {
      geoJSONLayer.setStyle(style);
      geoJSONLayer.eachLayer(function(layer){
        var subLayers = (!layer._layers) ? {'x': layer} : layer._layers;
        for (var i in subLayers) {
          if (subLayers[i]._popup) {
            subLayers[i]._popup.setContent(popupContent(layer.feature))
            subLayers[i]._popup.update();
          }
        }
      });
    }
  }
})()

$(document).ready(function(){
    RTEI.map.init();

    $('.indicator-switcher input').on('click', function(){
      if (this.value != RTEI.map.currentIndex) {
        RTEI.map.currentIndex = this.value;
        RTEI.map.currentIndexLabel = $('label[for="' + this.id + '"]').text();
        if (this.id.indexOf('.') !== -1) {
          className = $('label[for="' + this.id.substring(0, this.id.indexOf('.')) + '"]').text();
        } else {
          className = RTEI.map.currentIndexLabel;
        }
        $('body').attr('class', 'template-explore-map ' + className.toLowerCase().replace(' ', '_'));
        RTEI.map.refresh();
      }
    });
});
