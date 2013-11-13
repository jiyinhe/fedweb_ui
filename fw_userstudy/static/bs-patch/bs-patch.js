function affixWidth() {
    // ensure the affix element maintains it width
    var affix = $(".affix-left");
    var width = affix.width();
    affix.width(width);	

    affix = $(".affix-right");
    width = affix.width();
    affix.width(width);
}


$(document).ready(function () {

    affixWidth();

});
