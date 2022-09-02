jQuery(document).ready(function( $ ) {
  var average_gigs, average_price, unit, average_to_mb;
  var url = estimatorjs.noc_path;
  var rangeSlider = function(){
    var slider = $('.range-slider'),
        range = $('.range-slider__range'),
        value = $('.range-slider__value');

    slider.each(function () {

      value.each(function () {
        var value = $(this).prev().attr('value');
        $(this).html(value);
      });

      range.on('input', function () {
        $(this).next(value).html(this.value);
      });
    });
  };

  rangeSlider();

  $.post(url, function(data) {
    var convert = convertGB(Math.round(data)),
        pBar = jQuery("#price-bar-average .progress"),
        totalSize,
        percent;
    average_gigs = convert[0];
    unit = convert[1];
    average_price = convert[2];
    average_to_mb = average_gigs * 1000;
    $(".progress-title .average-price").text(average_price);
    $(".progress-title span[data-type='average-size']").text(average_gigs);
    $(".progress-title span[data-type='average-usage-unit']").text(unit);

    if (unit === "MB") {
      percent = average_gigs / 1000000
    }

    if (unit === "GB") {
      percent = average_gigs / 1000
    }

    if (unit === "TB") {
      percent = average_gigs / 1
    }

    totalSize = Math.round(10 * average_gigs) / 10;
    pBar.css('width', percent*100+"%");
  });

  function convertGB(gigabytes) {
    var idx, mb, units, price;
    var basePrice = 19.95;
    var perGigPrice = 0.2;

    for (
        units = ["MB", "GB", "TB", "PB", "EB", "ZB", "YB"],
            mb = 1000 * gigabytes,
            idx = 0;
        mb > 1000;

    ) {
      (mb /= 1000), idx++;
    }

    price = (mb * perGigPrice + basePrice).toFixed(2);

    return [mb, units[idx], price];
  }
}),

    function estimationInit() {
      var basePrice = 19.95;
      var perGigPrice = 0.2;
      var currentGigs = 0;

      this.DataCalculator = (function() {
        function DataCalculator() {}
        return (
            (DataCalculator.setMultiplier = function(key, value) {
              var row = DataCategories[key];
              var valid_key = this.__validate_key(key);

              if (valid_key) {
                row.unitMultiplier = value;
                return this.__update_ui();
              } else {
                return void 0;
              }
            }),
                (DataCalculator.__validate_key = function(key) {
                  return null != DataCategories[key]
                      ? !0
                      : (console.error(
                          'Key "' + key + '" does not exist in DataCategories'
                      ),
                          !1);
                }),
                (DataCalculator.__publish_size = function(gigabytes, percentage) {
                  var pBar = jQuery("#price-bar-estimate .progress"),
                      price,
                      gigsUsedForPrice,
                      gb = this.__grabMbAndUnit(gigabytes)[0],
                      unit = this.__grabMbAndUnit(gigabytes)[1],
                      totalSize,
                      gigsUsedForPrice;

                  gigsUsedForPrice = gb;
                  if (unit == "MB") {
                    gigsUsedForPrice = gb / 1000;
                  }

                  if (unit == "TB") {
                    gigsUsedForPrice = gb * 1000;
                  }

                  totalSize = Math.round(10 * gb) / 10;

                  if (gigsUsedForPrice >= 1000) {
                    gigsUsedForPrice = 1000;
                    totalSize = 1;
                    unit = "TB";
                  }

                  currentGigs = gigsUsedForPrice;

                  price = (gigsUsedForPrice * perGigPrice + basePrice).toFixed(2);

                  if (currentGigs <= gigsUsedForPrice) {
                    pBar.css('width', percentage+"%");
                  }

                  if (currentGigs >= 1000) {
                    totalSize = 1;
                    unit += "+";
                    price += "+";
                  }
                  return (
                      jQuery('span.estimate-price').text(price),
                          jQuery('span.estimate-size').text(totalSize),
                          jQuery('span.estimate-unit').text(unit)
                  );
                }),
                (DataCalculator.__update_ui = function() {
                  var key,
                      percentage,
                      row,
                      total = 0;

                  for (key in DataCategories) {
                    row = DataCategories[key];
                    total += row.calculateUsage();
                  }

                  var percentage = Math.round((total / 1024) * 1e3) / 10;
                  return this.__publish_size(total, percentage);
                }),
                (DataCalculator.__grabMbAndUnit = function(gigabytes) {
                  var idx, mb, units;

                  for (
                      units = ["MB", "GB", "TB", "PB", "EB", "ZB", "YB"],
                          mb = 1024 * gigabytes,
                          idx = 0;
                      mb > 1024;

                  ) {
                    (mb /= 1024), idx++;
                  }

                  var unit = units[idx];
                  return [mb, unit];
                }),
                DataCalculator
        );
      })();
    }.call(this),
    function() {
      jQuery('.range-slider__range').on('input', function() {
        var key;
        key = jQuery(this).data('key');

        if (null == key) {
          return console.error(
              "missing input with proper key"
          );
        }

        return DataCalculator.setMultiplier(key, this.value);
      });
    }.call(this),
    function() {
      this.DataCategories = {
        web: {
          category: "web",
          calculateUsage: function() {
            return 0.015 * this.unitMultiplier * daysInThisMonth();
          },
          unitMax: 24,
          unitMultiplier: 0,
          unitStep: 1
        },
        social: {
          category: "social",
          calculateUsage: function() {
            return 0.094 * this.unitMultiplier * daysInThisMonth();
          },
          unitMax: 24,
          unitMultiplier: 0,
          unitStep: 1
        },
        email: {
          category: "email",
          calculateUsage: function() {
            return (0.4 / 1024) * this.unitMultiplier * daysInThisMonth();
          },
          unitMax: 10000,
          unitMultiplier: 0,
          unitStep: 1
        },
        games: {
          category: "games",
          calculateUsage: function() {
            return 0.034 * this.unitMultiplier * daysInThisMonth();
          },
          unitMax: 24,
          unitMultiplier: 0,
          unitStep: 1
        },
        music: {
          category: "music",
          calculateUsage: function() {
            return 0.055 * this.unitMultiplier * daysInThisMonth();
          },
          unitMax: 24,
          unitMultiplier: 0,
          unitStep: 1
        },
        streamSD: {
          category: "streamSD",
          calculateUsage: function() {
            return 1 * this.unitMultiplier * daysInThisMonth();
          },
          unitMax: 24,
          unitMultiplier: 0,
          unitStep: 1
        },
        streamHD: {
          category: "streamHD",
          calculateUsage: function() {
            return 3 * this.unitMultiplier * daysInThisMonth();
          },
          unitMax: 24,
          unitMultiplier: 0,
          unitStep: 1
        },
        stream4K: {
          category: "stream4K",
          calculateUsage: function() {
            return 8 * this.unitMultiplier * daysInThisMonth();
          },
          unitMax: 24,
          unitMultiplier: 0,
          unitStep: 1
        },
        cloudcams: {
          category: "cloudcams",
          calculateUsage: function() {
            return 60 * this.unitMultiplier;
          },
          unitMax: -1,
          unitMultiplier: 0,
          unitStep: 1
        }
      };
    }.call(this);

function daysInThisMonth() {
  var now = new Date();
  return new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
}
