function affixWidth() {
    // ensure the affix element maintains it width
    var affixleft = $(".affix-left");
    var widthleft = affixleft.width();
    affixleft.width(widthleft);	

    var affixright = $(".affix-right");
    var widthright = affixright.width();
    var affixright.width(widthright);
}


$(document).ready(function () {

    affixWidth();

});
