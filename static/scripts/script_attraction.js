// 第三周的提前作業

console.log("Hello world!");

console.log(window.location.search);

function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Get the 'id' from the query parameters
const attractionId = getQueryParam('id');

console.log(attractionId);

console.log(window.location);

console.log(window.location.href);

console.log(window.location.pathname);

let pathName = window.location.pathname;

match = pathName.match(/attraction\/(.+?)(\/)?$/);

let attractionID;

if (match && match[1]){
    console.log(match[1]);
    attractionID = match[1];
}

async function getAttractionData(url){
    console.log(url);
    const response = await fetch(url);
    const response_json = await response.json();
    console.log(response_json);
    return response_json;
}

let attractionurlBase = "/api/attraction/";

async function getAttractionPage(attractionID){
    console.log("running here");
    response_json = await getAttractionData(attractionurlBase+attractionID);
    console.log(response_json);
    let descriptionDiv = document.querySelector(".text-block-6");
    descriptionDiv.innerHTML = response_json.data.description;
    let addressDiv = document.querySelector(".text-block-7");
    addressDiv.innerHTML = response_json.data.address;
    let transportDiv = document.querySelector(".text-block-8");
    transportDiv.innerHTML = response_json.data.transport;

    let attractionDiv = document.querySelector(".attraction-text");
    attractionDiv.innerHTML = response_json.data.name;
    let categorySpan = document.querySelector(".category-text");
    categorySpan.innerHTML = response_json.data.category;
    let mrtSpan = document.querySelector(".mrt-text");
    mrtSpan.innerHTML = response_json.data.mrt;
}

getAttractionPage(attractionID);


// slideshow
let slideIndex = 0;
showSlides(slideIndex);

function showSlides(index){
    let slides = document.querySelectorAll(".slides-picture");
    let totalSlides = slides.length;

    if (index < 0){
        // mod(n,m) when n<0 in JS: mod(n,m) = ((n % m) + m) % m
        index = ((index % totalSlides) + totalSlides) % totalSlides;
    }
    else if (index >= totalSlides){
        index %= totalSlides;
    }

    console.log("index:", index);

    for (slideNo = 0; slideNo < totalSlides; slideNo++){
        if (slideNo === index){
            slides[slideNo].style.display = "block";
            console.log("Activating slide:", slideNo);
        }
        else{
            slides[slideNo].style.display = "none";
        }
    }
}

function plusSlides(noOfslides){
    slideIndex += noOfslides;
    console.log("Slide no.:", slideIndex);
    showSlides(slideIndex);
}


//Below for test purposes!!
// let data = fetch("https://api.github.com").then((response)=>response.json()).then((response2)=>console.log(response2));
// console.log(data);

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


document.querySelector("#travel_date").addEventListener("change", function(){
    document.querySelector("#date-text").textContent = document.querySelector("#travel_date").value;
    }
);

