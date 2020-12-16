function goToNextAnchor() {
    var anchors = document.body.getElementsByTagName("a");
    var loc = window.location.href.replace(/#.*/,'');
    var nextAnchorName;

    // Get name of the current anchor from the hash
    // if there is one
    var anchorName = window.location.hash.replace(/#/,'');

    // If there is an anchor name...
    if (anchorName) {

        // Find current element in anchor list, then
        // get next anchor name, or if at last anchor, set to first
        for (var i=0, iLen=anchors.length; i<iLen; i++) {
            if (anchors[i].name == anchorName) {
                nextAnchorName = anchors[i++ % iLen].name;
                break;
            }
        }
    }

    // If there was no anchorName or no match,
    // set nextAnchorName to first anchor name
    if (!nextAnchorName) {
        nextAnchorName = anchors[0].name;
    }

    // Go to new URL
    window.location.href = loc + '#' + nextAnchorName;
}

function goToNextElementByClass(className = 'level1', delta) {
    var anchors = document.body.getElementsByClassName(className);
    anchors = Array.from(anchors); //convert to array
    anchors = anchors.filter(function(value, index, arr){ 
        return !value.innerText.startsWith('draws'); // hack to skip "draws: 0" anchors
    });    
    var loc = window.location.href.replace(/#.*/,'');
    var nextAnchorName;

    // Get name of the current anchor from the hash
    // if there is one
    var currentAnchorName = window.location.hash;

    // If there is an anchor name...
    if (currentAnchorName)
    {
        // Find current element in anchor list, then
        // get next anchor name, or if at last anchor, set to first
        for (var i=0, iLen=anchors.length; i<iLen; i++) {
            if (anchors[i].hash == currentAnchorName) {
                let nextId = i+delta;
                if (nextId < 0) nextId = 0;
                if (nextId > anchors.length - 1) nextId = anchors.length - 1;
                nextAnchorName = anchors[nextId].hash;
                break;
            }
        }
    }

    // If there was no anchorName or no match,
    // set nextAnchorName to first anchor name
    if (!nextAnchorName) {
        nextAnchorName = anchors[0].hash;
    }

    // Go to new URL
    window.location.href = loc + nextAnchorName;
}
    
document.addEventListener('keypress', logKey);

function logKey(e) {
    // https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/keyCode
    // console.log(e);
    if (e.key == "p") goToNextElementByClass('level1', 1);
    if (e.key == "P") goToNextElementByClass('level1', -1);
    if (e.key == "s") goToNextElementByClass('level2', 1);
    if (e.key == "S") goToNextElementByClass('level2', -1);
    if (e.key == "d") goToNextElementByClass('level3', 1);
    if (e.key == "D") goToNextElementByClass('level3', -1);
    if (e.key == "0") goToNextElementByClass('level1', -1000000000000000);
}

function onMarkdeepLoaded() {
    let images = document.body.getElementsByTagName('img');
    for (let image of images) {
        image.parentElement.removeAttribute('href');
    }
}

markdeepOptions={tocStyle:'long', onLoad:onMarkdeepLoaded};