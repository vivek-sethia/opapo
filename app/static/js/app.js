/*** First Chart  ***/
$(document).ready(function() {

    function isInStock(availability) {
        availability = availability.toLowerCase();
        return availability && ((availability.indexOf('in stock') !== -1 || availability.indexOf('available') !== -1) && availability.indexOf(' not ') === -1);
    }

    function getCost(shipping) {
        var cost;
        shipping = shipping.toLowerCase();
        if (shipping && shipping.indexOf('free') !== -1) {
            cost = 'FREE';
        }
        return cost;
    }

    $.getJSON("../data.json", function(data) {

        var star, price_arr, ratings = [], amazon_chart, ebay_chart, amazon_avg_rating;

        console.log(data);

        /*Set the details of the product*/
        $('#title').text(data.amazon.title);

        price_arr = (data.amazon.price).split(".");

        $('#amazon_price').text(price_arr[0]);
        $('#amazon_price_cent').text(price_arr[1]);
        $('#amazon_shipping_cost').text(getCost(data.amazon.shipping));

        if(isInStock(data.amazon.availability || '')) {
            $('#amazon_availability').attr('src', '../static/img/yes.png');
        }
        $('#amazon_review_count').text(data.amazon.rating.review_count + ' reviews');
        $('#amazon_product_img').attr('src', data.amazon.image);
        $('#amazon_product_link').attr('href', data.amazon.product_link);

        amazon_avg_rating = (parseFloat(data.amazon.rating.average.trim('out of 5 stars'))/5)*100;
        $('.amazon_features .star-ratings-sprite-rating').css('width', amazon_avg_rating);

        price_arr = (data.ebay.price).split(".");

        $('#ebay_price').text(price_arr[0]);
        $('#ebay_price_cent').text(price_arr[1]);
        $('#ebay_shipping_cost').text(data.ebay.shippingCost);


        if(isInStock(data.ebay.availability || '')) {
            $('#ebay_availability').attr('src', '../static/img/yes.png');
        }
        $('#ebay_review_count').text(data.ebay.rating.review_count);
        $('#ebay_product_img').attr('src', data.ebay.image);
        $('#ebay_product_link').attr('href', data.ebay.product_link);

        /*Format the ratings as per data format of charts*/
        for(star in data.amazon.rating.stats) {
            ratings.push({
                name: star,
                y: parseFloat(data.amazon.rating.stats[star])
            })
        }

        new Highcharts.Chart({
            chart: {
                renderTo: 'load',
                margin: [0, 0, 0, 0],
                backgroundColor: null,
                plotBackgroundColor: 'none'
            },
            title: {
                text: null
            },
            tooltip: {
                formatter: function() {
                    return this.point.name + ': ' + this.y + ' %';
                }
            },
            legend: {
                enabled: true,
                align: 'right',
                layout: 'vertical',
                 itemStyle: {
                    color: 'white',
                    font: '12pt Trebuchet MS, Verdana, sans-serif'
                 }
            },
            plotOptions: {
                pie: {
                    showInLegend: true
                }
            },
            series: [{
                borderWidth: 2,
                borderColor: '#F1F3EB',
                shadow: false,
                type: 'pie',
                name: 'Income',
                innerSize: '65%',
                data: ratings,
                dataLabels: {
                    enabled: false,
                    color: '#000000',
                    connectorColor: '#000000'
                }
            }]
        });

        /*ebay_chart = new Highcharts.Chart({
            chart: {
                renderTo: 'space',
                margin: [0, 0, 0, 0],
                backgroundColor: null,
                plotBackgroundColor: 'none'
            },
            title: {
                text: null
            },
            tooltip: {
                formatter: function() {
                    return this.point.name + ': ' + this.y + ' %';
                }
            },
            series: [{
                borderWidth: 2,
                borderColor: '#F1F3EB',
                shadow: false,
                type: 'pie',
                name: 'SiteInfo',
                innerSize: '65%',
                data: [{
                    name: 'Used',
                    y: 65.0
                }, {
                    name: 'Rest',
                    y: 35.0
                }],
                dataLabels: {
                    enabled: false,
                    connectorColor: '#000000'
                }
            }]
        });*/

        new Highcharts.Chart({
            chart: {
                renderTo: 'container',
                type: 'gauge',
                plotBackgroundColor: null,
                plotBackgroundImage: null,
                plotBorderWidth: 0,
                plotShadow: false
            },
            title: {
                text: 'Emotional Meter'
            },
            pane: {
                startAngle: -150,
                endAngle: 150,
                background: [{
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, '#FFF'],
                            [1, '#333']
                        ]
                    },
                    borderWidth: 0,
                    outerRadius: '109%'
                }, {
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, '#333'],
                            [1, '#FFF']
                        ]
                    },
                    borderWidth: 1,
                    outerRadius: '107%'
                }, {
                    // default background
                }, {
                    backgroundColor: '#DDD',
                    borderWidth: 0,
                    outerRadius: '105%',
                    innerRadius: '103%'
                }]
            },
            // the value axis
            yAxis: {
                min: -4,
                max: 4,

                minorTickInterval: 'auto',
                minorTickWidth: 1,
                minorTickLength: 10,
                minorTickPosition: 'inside',
                minorTickColor: '#666',

                tickPixelInterval: 30,
                tickWidth: 2,
                tickPosition: 'inside',
                tickLength: 10,
                tickColor: '#666',
                labels: {
                    step: 2,
                    rotation: 'auto'
                },
                title: {
                    text: ''
                },
                plotBands: [{
                    from: -4,
                    to: -1,
                    color: '#DF5353' // red
                }, {
                    from: -1,
                    to: 1,
                    color: '#DDDF0D' // yellow
                }, {
                    from: 1,
                    to: 4,
                    color: '#55BF3B' // green
                }]
            },
            series: [{
                name: 'Sentiment',
                data: [data.amazon.overall_sentiment],
                tooltip: {
                    valueSuffix: ''
                }
            }]
        });
    });
});