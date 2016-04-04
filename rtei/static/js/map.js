var RTEI = RTEI || {}
RTEI.map = (function() {

  var homepage = window.location.href.indexOf('explore/map') === -1;

  // get color depending on the selected index
  function getColor(score) {
    if (!score) {
      if (homepage) {
        return '#595a5b';
      } else {
        return '#bebebd';
      }
    }
    score = parseFloat(score);
    return score > 80 ? '#ad2429' :
           score > 60 ? '#df4439' :
           score > 40 ? '#f97b5d' :
           score > 20 ? '#fbb89d' :
           score > 0  ? '#fde8dd' :
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

      RTEI.map.map = L.map('map', {
        attributionControl: false,
        zoomControl: false
      }).setView([40, 10], 1.5);
      L.control.zoom({position: 'topright'}).addTo(RTEI.map.map);

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
        RTEI.map.currentIndexLabel = $('label[for="' + this.id + '"]').html();
        RTEI.map.refresh();
      }
    });
});
