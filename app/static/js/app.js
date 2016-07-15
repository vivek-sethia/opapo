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

        var star, price_arr, ratings = [], amazon_avg_rating, ebay_avg_rating,
            rating_stats = {
                'amazon': {'renderTo': 'amazon_rating_stats', 'data': []},
                'ebay': {'renderTo': 'ebay_rating_stats', 'data': []}
            },
            sentiments = {
                'amazon': {'renderTo': 'amazon_sentiment_chart', 'data': data.amazon.overall_sentiment || 0},
                'ebay': {'renderTo': 'ebay_sentiment_chart', 'data': data.ebay.overall_sentiment || 0}
            },
            tone_details = {
                'amazon': data.amazon.tones || {},
                'ebay': data.ebay.tones || {}
            };

        console.log(data);

        /*Set the details of the product*/
        $('#title').text(data.amazon.title);

        price_arr = (data.amazon.price).split(".");

        $('#amazon_price').text(price_arr[0]);
        $('#amazon_price_cent').text(price_arr[1]);
        $('#amazon_shipping_cost').text(getCost(data.amazon.shipping));
        $('#amazon_merchant_feedback').text(data.amazon.merchant);

        if(isInStock(data.amazon.availability || '')) {
            $('#amazon_availability').attr('src', '../static/img/yes.png');
        }
        if(data.amazon.rating.review_count)
            $('#amazon_review_count').text(data.amazon.rating.review_count + ' reviews');

        $('#amazon_product_img').attr('src', data.amazon.image);
        $('#amazon_product_link').attr('href', data.amazon.product_link);

        if(data.amazon.rating.average) {
            amazon_avg_rating = (parseFloat(data.amazon.rating.average.trim('out of 5 stars'))/5)*100;
            $('.amazon_features .star-ratings-sprite-rating').css('width', amazon_avg_rating + '%');
        }

        price_arr = (data.ebay.price).split(".");

        $('#ebay_price').text(price_arr[0]);
        $('#ebay_price_cent').text(price_arr[1]);
        $('#ebay_shipping_cost').text(data.ebay.shippingCost);

        if(data.ebay.merchant)
            $('#ebay_merchant_feedback').text(data.ebay.merchant['name'] + ' (' +
                data.ebay.merchant['sold_quantity'] + 'items sold & ' + data.ebay.merchant['feedback']+ ')');

        if(isInStock(data.ebay.availability || '')) {
            $('#ebay_availability').attr('src', '../static/img/yes.png');
        }

        if(data.ebay.rating.review_count)
            $('#ebay_review_count').text(data.ebay.rating.review_count + ' reviews');

        $('#ebay_product_img').attr('src', data.ebay.image);
        $('#ebay_product_link').attr('href', data.ebay.product_link);

        if(data.ebay.rating.average) {
            ebay_avg_rating = (parseFloat(data.ebay.rating.average.trim('out of 5 stars'))/5)*100;
            $('.ebay_features .star-ratings-sprite-rating').css('width', ebay_avg_rating + '%');
        }

        if(data.amazon.rating.stats) {
            /*Format the ratings as per data format of charts*/
            $.each(data.amazon.rating.stats, function(star, rating) {
                rating_stats['amazon'].data.push({
                    name: star,
                    y: parseFloat(rating)
                })
            });
        }
        if(data.ebay.rating.stats) {
            /*Format the ratings as per data format of charts*/
            $.each(data.ebay.rating.stats, function(star, rating) {
                rating_stats['ebay'].data.push({
                    name: star,
                    y: parseFloat(rating)
                })
            });
        }

        $.each(rating_stats, function(index, stat) {
            /*Donut chart for distribution of rating in reviews*/
            new Highcharts.Chart({
                chart: {
                    renderTo: stat['renderTo'],
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
                    data: stat['data'],
                    dataLabels: {
                        enabled: false,
                        color: '#000000',
                        connectorColor: '#000000'
                    }
                }]
            });
        });

        $.each(sentiments, function(index, sentiment) {
            /*Gauge chart for overall sentiment of reviews*/
            new Highcharts.Chart({
                chart: {
                    renderTo: sentiment['renderTo'],
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
                    data: [sentiment['data']],
                    tooltip: {
                        valueSuffix: ''
                    }
                }]
            });
        });

        $.each(tone_details, function(index, tones) {
            $.each(tones, function(toneName, tone) {
                var title = toneName, color, colorByPoint = false;

                switch(toneName) {
                    case 'writing':
                        title = 'language style';
                        color = '#274b5f';
                        break;
                    case 'social':
                        title = 'social tendencies';
                        color = '#1cb4a0';
                        break;
                    case 'emotion':
                        color = ['#e80521','#592684', '#325e2b','#ffd629', '#086db2' ];
                        colorByPoint = true;
                        break;
                }

                /*Horizontal bar chart for various tone categories of reviews*/
                new Highcharts.Chart({
                    chart: {
                        type: 'bar',
                        renderTo: index + '_' + toneName + '_chart'
                    },
                    title: {
                        text: title.toUpperCase()
                    },
                    xAxis: {
                        categories: tone['tone_names'],
                        title: {
                            text: null
                        }
                    },
                    yAxis: {
                        gridLineWidth: 0,
                        minorGridLineWidth: 0,
                        min: 0,
                        max: 1,
                        title: {
                            text:'',
                            align: 'high'
                        },
                        labels: {
                            overflow: 'justify',
                            enabled: false
                        }
                    },
                    tooltip: {
                        valueSuffix: ''
                    },
                    plotOptions: {
                        bar: {
                            dataLabels: {
                                enabled: true
                            }
                        },
                         series: {
                             colorByPoint: colorByPoint
                         }
                    },
                    legend: {
                        enabled: false,
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'top',
                        x: -40,
                        y: 80,
                        floating: true,
                        borderWidth: 1,
                        backgroundColor: ((Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'),
                        shadow: true
                    },
                    colors: color,
                    credits: {
                        enabled: false
                    },
                    series: [{
                        name: toneName,
                        data: tone['scores'],
                        color: color
                    }]
                });
            });
        });

    });
});