/*** First Chart  ***/
$(document).ready(function() {

    function isInStock(availability) {
        availability = availability.toLowerCase();
        return availability && ((availability.indexOf('in stock') !== -1 || availability.indexOf('available') !== -1) && availability.indexOf(' not ') === -1);
    }

    $.getJSON("../data.json", function(data) {

        var star, ratings = [], amazon_chart, ebay_chart, amazon_avg_rating;

        console.log(data);

        /*Set the details of the product*/
        $('#title').text(data.amazon.title);

        $('#amazon_price').text(data.amazon.price);

        if(isInStock(data.amazon.availability || '')) {
            $('#amazon_availability').attr('src', '../static/img/yes.png');
        }
        $('#amazon_review_count').text(data.amazon.rating.review_count);
        $('#amazon_product_img').attr('src', data.amazon.image);
        $('#amazon_product_link').attr('href', data.amazon.product_link);

        amazon_avg_rating = (parseFloat(data.amazon.rating.average.trim('out of 5 stars'))/5)*100;
        $('.amazon_features .star-ratings-sprite-rating').css('width', amazon_avg_rating);

        $('#ebay_price').text(data.ebay.price);

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

        amazon_chart = new Highcharts.Chart({
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

        ebay_chart = new Highcharts.Chart({
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
        });

        $('#container').highcharts({
            chart: {
                type: 'scatter',
                zoomType: 'xy'
            },
            title: {
                text: 'Rating Versus Sentiment'
            },
            subtitle: {
                text: 'Latest 30 reviews'
            },
            xAxis: {
                title: {
                    enabled: true,
                    text: 'Sentiment ()'
                },
                startOnTick: true,
                endOnTick: true,
                showLastLabel: true
            },
            yAxis: {
                title: {
                    text: 'Rating (star)'
                }
            },
            legend: {
                layout: 'vertical',
                align: 'left',
                verticalAlign: 'top',
                x: 100,
                y: 70,
                floating: true,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                borderWidth: 1
            },
            plotOptions: {
                scatter: {
                    marker: {
                        radius: 5,
                        states: {
                            hover: {
                                enabled: true,
                                lineColor: 'rgb(100,100,100)'
                            }
                        }
                    },
                    states: {
                        hover: {
                            marker: {
                                enabled: false
                            }
                        }
                    },
                    tooltip: {
                        headerFormat: '<b>{series.name}</b><br>'
                        //pointFormat: '{point.x} cm, {point.y} kg'
                    }
                }
            },
            series: data.amazon.review_sentiments
        });
    });
});