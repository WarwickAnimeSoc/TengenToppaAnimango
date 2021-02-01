/* Custom javascript for the site */

/* Archive image resize detection */
/* This function is used in the archive app to check if an image has been resized. */
function archiveSizeCheck() {
    let image = document.getElementById('archiveImage');
    if (image) {
        /* If image was null then archive item was a video. Video's can be viewed fullscreen via the controls, so
        * a re-size notification isn't needed. */
        if (image.clientWidth !== image.naturalWidth) {
            let messagesDiv = document.getElementById('messagesDiv');
            let resizeMessage = document.createElement('div');
            let messageText = 'This image has been re-sized! <a href="' + image.src + '">Click here</a> for the original image.'
            resizeMessage.className = 'alert alert-primary';
            resizeMessage.innerHTML = messageText;
            messagesDiv.appendChild(resizeMessage);
        }
    }
}

/* Error page divergence meter */
/* This function will generate a divergence meter string in the format 0.XXXXXX, it's used in the error pages. */
function writeDivergenceMeter() {
    let divergenceMeter = document.getElementById('divergenceMeter');
    let divergenceNumber = Math.random();
    divergenceMeter.innerText = divergenceNumber.toString().slice(0, 8);
}

/* Multi element carousel next */
/* Used to move items left on a multi element carousel */
function multiCarouselNext() {
    /* Move first child to end and hide */
    let multiCarouselDiv = $('#multiCarousel')
    let firstChild = multiCarouselDiv.children(':first-child')
    firstChild.css({display: 'none'});
    multiCarouselDiv.append(firstChild)

    /* Un-hide first hidden element */
    multiCarouselDiv.children(':hidden').first().css({display: 'block'})
}

/* Multi element carousel prev */
/* Used to move items right on a multi element carousel */
function multiCarouselPrev() {
    /* Move first child to end and hide */
    let multiCarouselDiv = $('#multiCarousel')
    let lastChild = multiCarouselDiv.children(':last-child')
    lastChild.css({display: 'block'})
    multiCarouselDiv.prepend(lastChild)

    /* Un-hide first hidden element */
    multiCarouselDiv.children(':visible').last().css({display: 'none'})
}

/* Article image scaling setup */
/* Adds the scaleImage function to the onclick attribute of each image in the page */
function addScaleImageOnClick() {
    let article = $('#article-content')
    article.find('img').attr('onClick', 'scaleImage(this);').css({'width': '20%', 'max-width': '100%', 'cursor': 'pointer'});
}

/* Article view image scaling */
/* Used to toggle the width of an image when clicked */
function scaleImage(image) {
    let width = image.style.width;

    if (width === '20%') {
        image.style.width = '';
    } else {
        image.style.width = '20%';
    }
}