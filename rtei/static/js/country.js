var RTEI = RTEI || {}
RTEI.country = (function() {
})()

$(document).ready(function(){
    $('#available-countries').on('change', function(){
      if (this.value) {
        window.location = '/explore/rtei-country?id=' + this.value;
      }
    });
});

