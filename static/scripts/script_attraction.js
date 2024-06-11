// function getQueryParam(param) {
//     const urlParams = new URLSearchParams(window.location.search);
//     return urlParams.get(param);
// }

// Get attraction ID from the URL(window object)
let pathName = window.location.pathname;
let attractionID;
match = pathName.match(/attraction\/(.+?)(\/)?$/); //把pathname /attraction之後的字串取出來放在match[1]
console.log("Reading and matching URL by Regex:", match);
if (match && match[1]){
    attractionID = match[1];
}
else{
    alert("Attraction not found!");
}

// Fetch any url and parse as json.
async function getAttractionData(url){
    console.log("Fetching URL:", url);
    const response = await fetch(url);
    const response_json = await response.json();
    return response_json;
}

// Fetch and render content based on attraction ID + base URL.
async function getAttractionPage(attractionID){
    let attractionurlBase = "/api/attraction/";
    response_json = await getAttractionData(attractionurlBase+attractionID);
    console.log("Obtained response:", response_json);

    // render text in the lower div
    let descriptionDiv = document.querySelector(".text-block-6");
    descriptionDiv.innerHTML = response_json.data.description;
    let addressDiv = document.querySelector(".text-block-7");
    addressDiv.innerHTML = response_json.data.address;
    let transportDiv = document.querySelector(".text-block-8");
    transportDiv.innerHTML = response_json.data.transport;

    // render text in the top-right div
    let attractionDiv = document.querySelector(".attraction-text");
    attractionDiv.innerHTML = response_json.data.name;
    let categorySpan = document.querySelector(".category-text");
    categorySpan.innerHTML = response_json.data.category;
    let mrtSpan = document.querySelector(".mrt-text");
    mrtSpan.innerHTML = response_json.data.mrt;

    // render images for image scroll
    console.log("Total images received:", response_json.data.images.length);

    for (let i=0; i<response_json.data.images.length;i++){
        console.log("Loading image...");
        let pictureDiv = document.querySelector(".picture");
        const newPictureDiv = document.createElement("div");
        newPictureDiv.className = "slides-picture";
        const newPictureImg = document.createElement("img");
        newPictureImg.src = response_json.data.images[i];
        newPictureDiv.appendChild(newPictureImg);

        // console.log("Picture div check:", pictureDiv);
        // below method adds in the opposite order...
        // pictureDiv.prepend(newPictureDiv);
        
        // below method adds in the correct order
        let buttonElement = document.querySelector("#attraction-scroll-left");
        pictureDiv.insertBefore(newPictureDiv, buttonElement);
        // console.log("Added picture div!");

        // Add selection dots
        const newDotSpan = document.createElement("span");
        newDotSpan.className = "dot-button";
        newDotSpan.addEventListener('click', function(){
            slideIndex = i;
            showSlides(slideIndex);
        });

        let dotContainer = document.querySelector(".dot-button-container");
        dotContainer.append(newDotSpan);
    }
    let pictureDiv = document.querySelector(".picture");
    console.log("picture div check:", pictureDiv);
}

// Show a particular slide.
function showSlides(index){
    let slides = document.querySelectorAll(".slides-picture");
    let dots = document.querySelectorAll(".dot-button");
    let totalSlides = slides.length;

    if (index < 0){
        // mod(n,m) when n<0 in JS: mod(n,m) = ((n % m) + m) % m
        index = ((index % totalSlides) + totalSlides) % totalSlides;
    }
    else if (index >= totalSlides){
        index %= totalSlides;
    }
    // console.log("total slides:", totalSlides);
    // console.log("index:", index);

    for (slideNo = 0; slideNo < totalSlides; slideNo++){
        if (slideNo === index){
            slides[slideNo].style.display = "block";
            dots[slideNo].className = "dot-button selected";
            console.log("Activating slide:", slideNo);
        }
        else{
            slides[slideNo].style.display = "none";
            dots[slideNo].className = "dot-button";
        }
    }
}

// Left and Right Arrow buttons handling. 
function plusSlides(number){
    slideIndex += number;
    console.log("Internal slide no.:", slideIndex);
    showSlides(slideIndex);
}

// Tour price toggle function
function initializeTourPrice(){
    document.querySelector("#tour-price").textContent = "2000";

    document.querySelector("#morning").addEventListener("change", function(){
        if (this.checked){
            document.querySelector("#tour-price").textContent = "2000";
        }
    });
    
    document.querySelector("#afternoon").addEventListener("change", function(){
        if (this.checked){
            document.querySelector("#tour-price").textContent = "2500";
        }
    });    
}



// Initialize Attraction Page DOM
async function initializeAttraction(){
    await getAttractionPage(attractionID);
    slideIndex = 0;
    showSlides(slideIndex);
}

let slideIndex;
initializeAttraction();
initializeTourPrice();

