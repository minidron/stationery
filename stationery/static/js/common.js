$(function() {

  $('.carousel-sale').owlCarousel({
        loop: true,
        autoplay:true,
        autoplayTimeout:3000,
        items: 1,
        nav: false,
        smartSpeed: 700
    });

  $('a#go').click( function(event) {
        event.preventDefault();
        $('#overlay').fadeIn(400,
            function() {
                $('#modal_form')
                    .css('display', 'block')
                    .animate({opacity: 1, top: '50%'}, 200);
        });
    });
    $('#modal_close, #overlay').click( function() {
        $('#modal_form')
            .animate({opacity: 0, top: '45%'}, 200,
                function() {
                    $(this).css('display', 'none');
                    $('#overlay').fadeOut(400);
                }
            );
    });

  $('a#go_login').click( function(event) {
        event.preventDefault();
        $('#overlay').fadeIn(400,
            function() {
                $('#modal_form_2')
                    .css('display', 'block')
                    .animate({opacity: 1, top: '50%'}, 200);
        });
    });
    $('#modal_close_2, #overlay').click( function() {
        $('#modal_form_2')
            .animate({opacity: 0, top: '45%'}, 200,
                function() {
                    $(this).css('display', 'none');
                    $('#overlay').fadeOut(400);
                }
            );
    });

  $('.categories').owlCarousel({

        smartSpeed: 700,
        dots: false,
        navText: ['<i class="fa fa-angle-left"></i>', '<i class="fa fa-angle-right"></i>'],
        nav: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 1
            },
            480: {
                items: 2
            },
            800: {
                items: 4
            },
            1100: {
                items: 6
            }
        }
    });

    $('.cart-prices').owlCarousel({
        loop: false,
        smartSpeed: 700,
        dots: false,
        navText: ['<i class="fa fa-angle-left"></i>', '<i class="fa fa-angle-right"></i>'],
        nav: true,
        responsiveClass: true,
        responsive: {
            0: {
                items: 1
            },
            480: {
                items: 2
            },
            800: {
                items: 4
            },
            1100: {
                items: 6
            }
        }
    });

    jQuery("#slider").slider({
        min: parseInt(jQuery('#minCost').data('price')),
        max: parseInt(jQuery('#maxCost').data('price')),
        values: [parseInt(jQuery('#minCost').val()), parseInt(jQuery('#maxCost').val())],
        range: true,

        stop: function(event, ui) {
            jQuery("input#minCost").val(jQuery("#slider").slider("values", 0));
            jQuery("input#maxCost").val(jQuery("#slider").slider("values", 1));
        },

        slide: function(event, ui){
            jQuery("input#minCost").val(jQuery("#slider").slider("values", 0));
            jQuery("input#maxCost").val(jQuery("#slider").slider("values", 1));
        }
    });


  jQuery("input#minCost").change(function(){
    var value1=jQuery("input#minCost").val();
    var value2=jQuery("input#maxCost").val();

      if(parseInt(value1) > parseInt(value2)){
        value1 = value2;
        jQuery("input#minCost").val(value1);
    }
    jQuery("#slider").slider("values",0,value1);
  });


  jQuery("input#maxCost").change(function(){

    var value1=jQuery("input#minCost").val();
    var value2=jQuery("input#maxCost").val();

    if (value2 > 1000) { value2 = 1000; jQuery("input#maxCost").val(1000)}

    if(parseInt(value1) > parseInt(value2)){
        value2 = value1;
        jQuery("input#maxCost").val(value2);
    }
    jQuery("#slider").slider("values",1,value2);
  });



  // фильтрация ввода в поля
    // jQuery('input').keypress(function(event){
    //     var key, keyChar;
    //     if(!event) var event = window.event;

    //     if (event.keyCode) key = event.keyCode;
    //     else if(event.which) key = event.which;

    //     if(key==null || key==0 || key==8 || key==13 || key==9 || key==46 || key==37 || key==39 ) return true;
    //     keyChar=String.fromCharCode(key);

    //     if(!/\d/.test(keyChar)) return false;

    // });

    $('.view-product span').click(function() {
        var $elem = $(this);
        var $productList = $('.clearfix');
        $elem.toggleClass('active');
        $elem.siblings().toggleClass('active');
        $productList.toggleClass('table-layout products');
    });


    $(function() {
        $('ul.tabs__caption').each(function() {
            $(this).find('li').each(function(i) {
                $(this).click(function(){
                    $(this).addClass('active').siblings().removeClass('active').closest('div.tabs').find('div.tabs__content').removeClass('active').eq(i).addClass('active');
                });
            });
        });
    });

});


$(function() {
    $('#search-offer').devbridgeAutocomplete({
        serviceUrl: '/api/search_offer/',
        paramName: 'title',
        minChars: 2,
        maxHeight: 'auto',
        transformResult: function(response) {
            return {
                suggestions: $.map(JSON.parse(response), function(dataItem) {
                    return { value: dataItem.title, data: {
                        link: dataItem.url,
                        price: dataItem.price_retail,
                    }};
                })
            };
        },
        formatResult: function(suggestion, currentValue){
            return suggestion.value + '<div class="price">' + suggestion.data.price + '</div>';
        },
        onSelect: function (suggestion) {
            window.location.href = suggestion.data.link;
        },
    });
});
