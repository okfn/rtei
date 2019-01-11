var RTEI = RTEI || {}
RTEI.map = (function() {

  var homepage = window.location.href.indexOf('explore/map') === -1;

  var language = window.location.pathname.match(/^\/[a-zA-Z]{2}\//);

  var stripes = new L.StripePattern({
    angle: 45,
	spaceOpacity: 1,
	color: getBackgroundColor()
  });

  function getBackgroundColor() {
	if (homepage) {
	  return 'rgba(255,255,255,0.4)';
	} else {
	  return '#bebebd';
	}
  }

  // get color depending on the selected index
  function getColor(score) {

    var colors = RTEI.colors;


    if (!score || score == RTEI.insufficientData) {
	  return getBackgroundColor()
    }

    var palette;

    if (RTEI.map.currentIndex.substring(0, 1) == 't') {
      palette = colors.index;
    } else {
      palette = (RTEI.map.currentIndex.indexOf('.') !== -1) ?
        colors[RTEI.map.currentIndex.substring(0, RTEI.map.currentIndex.indexOf('.'))] :
        colors[RTEI.map.currentIndex];
    }
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
    if (feature.properties[RTEI.map.currentIndex] == RTEI.insufficientData) {
      _style = {
        color: bColour,
        fillPattern: stripes,
        fillOpacity: 1,
	    weight: 1
      }
    } else {
      _style = {
        weight: 1,
        opacity: 1,
        color: bColour,
        fillOpacity: 1,
        fillColor: getColor(feature.properties[RTEI.map.currentIndex]),
        fillPattern: null
      };
    }
    return _style;
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

    if (feature.properties[RTEI.map.currentIndex]) {
      content += ' <div class="country-score"><span>' + RTEI.map.currentIndexLabel + ': </span>' + RTEI.formatScore(feature.properties[RTEI.map.currentIndex]) + '</div>';
    } else  {
      content += ' <div class="no country-score" title="No data available">x</div>';
    }

    if (feature.properties.index) {
      content += ' <div class="country-name has-properties">' + feature.properties.name + '</div>';
      content += ' <div class="more-details"><a href="' + language + 'explore/rtei-country/?id=' + feature.properties.iso2 + '" title="Full country scores"></a></div>';
    } else {
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
          dragging: false,
          attributionControl: false,
          scrollWheelZoom: false,
          zoomControl: false
        }).setView([43, 15], 1.60);
        L.control.zoom({position: 'topright'}).addTo(RTEI.map.map);

      } else {
        RTEI.map.map = L.map('map', {
          attributionControl: false,
          scrollWheelZoom: false,
          zoomControl: false
        }).setView([55, 10], 1.5);
        L.control.zoom({position: 'topright'}).addTo(RTEI.map.map);
      }

      stripes.addTo(RTEI.map.map);

      // TODO: remove once we have the final data
      var random = Boolean((location.search.split('random=')[1]||'').split('&')[0]);
      var fileName = (random) ? 'countries_random.topojson': 'countries.topojson';
      geoJSONLayer = omnivore.topojson('/static/data/' + RTEI.year + '/' + fileName, null , customGeoJSONLayer)
        .addTo(RTEI.map.map);

    },

    // Refresh the countries layer symbology depending on the current index
    refresh: function() {
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
      var isTheme = (this.value.substring(0, 1) == 't');
      if (this.value != RTEI.map.currentIndex) {
        RTEI.map.currentIndex = this.value;
        RTEI.map.currentIndexLabel = $('label[for="' + this.id + '"]').text();

        RTEI.map.refresh();

        RTEI.showIndicators(this.value);
      }
    });

    // indicator list
    $("#indicators ul").slideUp().parent().addClass("has-children");
    $('#indicators .indicator').click(function(e){
      $(this).parent().children('ul').not(':animated').slideToggle().parent().toggleClass("open");
    });


});
