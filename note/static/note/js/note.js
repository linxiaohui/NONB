/** 侧边栏回到顶部 */
var rocket = $('#rocket');

$(window).on('scroll', debounce(slideTopSet, 300));

function debounce(func, wait) {
	var timeout;
	return function() {
		clearTimeout(timeout);
		timeout = setTimeout(func, wait);
	};
};

function slideTopSet() {
	var top = $(document).scrollTop();

	if (top > 200) {
		rocket.addClass('show');
	} else {
		rocket.removeClass('show');
	}
}
$(document).on('click', '#rocket', function(event) {
	rocket.addClass('move');
	$('body, html').animate({
		scrollTop: 0
	}, 800);
});
$(document).on('animationEnd', function() {
	setTimeout(function() {
		rocket.removeClass('move');
	}, 400);

});
$(document).on('webkitAnimationEnd', function() {
	setTimeout(function() {
		rocket.removeClass('move');
	}, 400);
});
