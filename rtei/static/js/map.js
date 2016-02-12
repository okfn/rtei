var RTEI = RTEI || {}
RTEI.map = (function() {

  var homepage = window.location.href.indexOf('explore/map') === -1;

  // get color depending on the selected index
  function getColor(score) {
    if (!score) {
      return '#B2B2B2';
    }
    score = parseFloat(score);
    return score > 80 ? '#E55066' :
           score > 60 ? '#D21E43' :
           score > 40 ? '#8D1423' :
           score > 20 ? '#48130B' :
           score > 0  ? '#120E05' :
                    '#B2B2B2';
  }

  function style(feature) {
    return {
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 1,
      fillColor: getColor(feature.properties.index)
    };
  }

  function highlightFeature(e) {
    var layer = e.target;
    layer.setStyle({
      weight: 2,
      color: '#666',
      dashArray: '',
      fillOpacity: 0.7
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

  function onEachFeature(feature, layer) {

    var content = ''
    content += '<div class="hoverinfo">';
    content += ' <h3>' + feature.properties.name + '</h3>';
    if (feature.properties.index) {
      content += ' <div class="country-score">Index: ' + feature.properties.index + '</div>';
      content += ' <div class="more-details">Click for more details</div>';
    } else {
      content += ' <div class="no-data">No data available</div>';
    }
    layer.bindPopup(content, {
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

    init: function() {

      RTEI.map.map = L.map('map', {
          attributionControl: false
      }).setView([10, 0], 2);

      geoJSONLayer = omnivore.topojson('/static/data/countries.topojson', null , customGeoJSONLayer)
        .addTo(RTEI.map.map);

    }
  }


})()

$(document).ready(function(){
    RTEI.map.init();
});
