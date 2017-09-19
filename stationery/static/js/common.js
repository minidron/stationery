$(function() {
    $.fn.equalHeights = function() {
        var maxHeight = 0,
            $this = $(this);

        $this.each( function() {
            var height = $(this).innerHeight();

            if ( height > maxHeight ) { maxHeight = height; }
        });

        return $this.css('height', maxHeight);
    };

    // auto-initialize plugin
    $('[data-equal]').each(function(){
        var $this = $(this),
            target = $this.data('equal');
        $this.find(target).equalHeights();
    });


	$('.carousel-sale').owlCarousel({
		loop: true,
		items: 1,
		nav: false,
		smartSpeed: 700
	});

	$('.cart-prices').owlCarousel({
		loop: true,
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
				items: 3
			},
			1100: {
				items: 4
			}
		}
	});

	$('button').on('click',function(e) {
    if ($(this).hasClass('grid')) {
        $('.blo').removeClass('col-sm-12 list').addClass('col-sm-4 grid');
        $('.vv').removeClass('col-sm-4').addClass('col-sm-12');
        $('.mom').removeClass('col-sm-8').addClass('col-sm-12');
        $('.mo').removeClass('col-sm-7').addClass('col-sm-12');
				$(".dad").css("display", "none");
				$(".na").css("display", "none");
				$(".part").css("display", "none");
				$(".col-sm-12").css("padding", "0");
    }
    else if($(this).hasClass('list')) {
        $('.blo').removeClass('col-sm-4 grid').addClass('col-sm-12 list');
				$('.vv').removeClass('col-sm-12').addClass('col-sm-4');
				$('.mom').removeClass('col-sm-12').addClass('col-sm-8');
				$('.mo').removeClass('col-sm-12').addClass('col-sm-7');
				$(".dad").css("display", "block");
				$(".na").css("display", "block");
				$(".part").css("display", "block");
    }
	});



	//Resize Window
	function onResize() {
		$('.foto').equalHeights();
	}onResize();
	window.onresize = function() {onResize()};


	jQuery("#slider").slider({
	min: 0,
	max: 1000,
	values: [0,1000],
	range: true,
	stop: function(event, ui) {
		jQuery("input#minCost").val(jQuery("#slider").slider("values",0));
		jQuery("input#maxCost").val(jQuery("#slider").slider("values",1));
    },
    slide: function(event, ui){
		jQuery("input#minCost").val(jQuery("#slider").slider("values",0));
		jQuery("input#maxCost").val(jQuery("#slider").slider("values",1));
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



});


$(function() {

	$(".popup").magnificPopup();

	});
$(function() {

	$(".popup1").magnificPopup();

	});

$('.message a').click(function(){
   $('form1').animate({height: "toggle", opacity: "toggle"}, "slow");
});
$('.message a').click(function(){
   $('form2').animate({height: "toggle", opacity: "toggle"}, "slow");
});

$(document).ready(function() {
		$('.down').click(function () {
			var $input = $(this).parent().find('input');
			var count = parseInt($input.val()) - 1;
			count = count < 1 ? 1 : count;
			$input.val(count);
			$input.change();
			return false;
		});
		$('.up').click(function () {
			var $input = $(this).parent().find('input');
			$input.val(parseInt($input.val()) + 1);
			$input.change();
			return false;
		});
	});

jQuery("#slider").slider({
	min: 0,
	max: 1000,
	values: [0,1000],
	range: true,
	stop: function(event, ui) {
		jQuery("input#minCost").val(jQuery("#slider").slider("values",0));
		jQuery("input#maxCost").val(jQuery("#slider").slider("values",1));
    },
    slide: function(event, ui){
		jQuery("input#minCost").val(jQuery("#slider").slider("values",0));
		jQuery("input#maxCost").val(jQuery("#slider").slider("values",1));
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

$(document).ready(function() {
	$('.block').on('click', '.extremum-click', function() {
		$(this).toggleClass('red').siblings('.extremum-slide').slideToggle(0);
	});
});

(function($) {
$(function() {

  $('ul.tabs__caption').each(function() {
    $(this).find('li').each(function(i) {
      $(this).click(function(){
        $(this).addClass('active').siblings().removeClass('active')
          .closest('div.tabs').find('div.tabs__content').removeClass('active').eq(i).addClass('active');
      });
    });
  });

})
})(jQuery)

