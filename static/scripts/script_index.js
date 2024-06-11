const bigBoxQty = 12;
let nextPage = null;
let keyword_document = null;
let initial_json;
let current_page = 0;
const attractions_per_load = 12;
let items_in_response;

// Fetch景點data相關函數: fetchNewAttractions, createBigBox, addAttractionData
// 根據輸入的page&keyword fetch景點data, 存到initial_json裡面
async function fetchNewAttractions(page_input, keyword_input = null){
    current_page = page_input;
    
    let params = new URLSearchParams({page: page_input});
    if (keyword_input){
        params.append('keyword', keyword_input)
    }
    let url = "api/attractions?" + params;
    console.log(`Fetching url: ${url}`);
    const response = await fetch(url);
    const response_json = await response.json();
    console.log("Fetch response:");
    console.log(response_json);
    nextPage = response_json.nextPage;
    console.log(`nextPage: ${nextPage}`);
    items_in_response = response_json.data.length;
    console.log(`Items in response: ${items_in_response}`);
    initial_json = response_json;
    return response_json;
}

// 根據response長度, 在DOM裡面生成新的Attraction box
function createBigBox(){
    for (let box=0;box<(items_in_response);box++){
        const bigBoxGroup = document.querySelector(".bigboxgroup");
        // const newAnchor = document.createElement("a");
        // newAnchor.className = "attraction-anchor";
        
        const newBox = document.createElement("div");
        newBox.className = "attraction";
        
        const newBoxImg = document.createElement("img");
        newBoxImg.src = "";
        newBoxImg.className = "bigboximage";
        newBox.appendChild(newBoxImg);

        const newTextBlock1 = document.createElement("div");
        newTextBlock1.className = "text-block-1";
        const newTextBlock1Text = document.createElement("div");
        newTextBlock1Text.className = "text-block-1-text white bold";
        newTextBlock1Text.textContent = "";
        newTextBlock1.appendChild(newTextBlock1Text);
        newBox.appendChild(newTextBlock1);

        const newTextBlock2 = document.createElement("div");
        newTextBlock2.className = "text-block-2";
        const newTextBlock2Text = document.createElement("div");
        newTextBlock2Text.className = "text-block-2-text body gray-50";
        newTextBlock2Text.textContent = "";
        newTextBlock2.appendChild(newTextBlock2Text);
        const newTextBlock3Text = document.createElement("div");
        newTextBlock3Text.className = "text-block-3-text body gray-50";
        newTextBlock3Text.textContent = "";
        newTextBlock2.appendChild(newTextBlock3Text);
        newBox.appendChild(newTextBlock2);

        const newAnchor = document.createElement("a");
        newAnchor.className = "attraction-anchor"
        newAnchor.appendChild(newBox);

        bigBoxGroup.appendChild(newAnchor);
    }
}

// 根據response長度, 在DOM各欄位加上的文字
function addAttractionData(){
    console.log(`Current page: ${current_page}, adding below data to DOM...`);
    console.log(initial_json);

    for (let box=0;box<(items_in_response);box++){
        // render text
        let box_no = current_page * attractions_per_load + box;

        let block1Text = document.querySelectorAll(".text-block-1-text")[box_no];
        let block1TextNode = document.createTextNode(`${initial_json.data[box].name}`);
        block1Text.appendChild(block1TextNode);

        // block2Text:mrt can be null
        let block2Text = document.querySelectorAll(".text-block-2-text")[box_no];
        let block2TextNode;
        if (initial_json.data[box].mrt){     
            block2TextNode = document.createTextNode(`${initial_json.data[box].mrt}`);
        }
        else{
            block2TextNode = document.createTextNode("無捷運資訊");
        }
        block2Text.appendChild(block2TextNode);

        let block3Text = document.querySelectorAll(".text-block-3-text")[box_no];
        let block3TextNode = document.createTextNode(`${initial_json.data[box].category}`);
        block3Text.appendChild(block3TextNode);
        
        // render images
        let block1Img = document.querySelectorAll(".bigboximage")[box_no];
        const block1imgURL = initial_json.data[box].images[0];
        block1Img.src = block1imgURL;

        let attractionAnchor = document.querySelectorAll(".attraction-anchor")[box_no];
        attractionAnchor.setAttribute('href', `attraction/${initial_json.data[box].id}`);
    }

    console.log("Added data to DOM.");

}


// 初始化相關函數: initializeJSON, initializeHorizontalScroll, initializeObserver, initializeSearchBarListener
// 一開始的資料撈取與render to DOM
async function initializeJSON(){
    console.log("Fetching initial data...");
    await fetchNewAttractions(page_input = 0, keyword_input = null);
    console.log("Fetched data check:");
    console.log(initial_json);
    addAttractionData();
    return initial_json;
}

// 初始化橫向卷軸Horizontal scroll
async function initializeHorizontalScroll(){
    const response = await fetch("api/mrts");
    const response_json = await response.json();
    mrt_stations = response_json.data.length;
    console.log(`Fetched MRT station data. Data length: ${mrt_stations}. Response data below:`);
    console.log(response_json);

    for (let mrt_no=0;mrt_no<(mrt_stations);mrt_no++){
    const horizontalScrollBar = document.querySelector(".horizontal-scroll-bar");
    const newSpan = document.createElement("span");
    newSpan.className = "mrt-item body";
    newSpan.textContent = response_json.data[mrt_no];

    horizontalScrollBar.appendChild(newSpan);
    }

    const horizontal_scrollbar_left = document.querySelector("#scroll-left");
    horizontal_scrollbar_left.addEventListener("click", function (event){
        document.querySelector(".horizontal-scroll-bar").scrollLeft -= 200;
    })

    const horizontal_scrollbar_right = document.querySelector("#scroll-right");
    horizontal_scrollbar_right.addEventListener("click", function (event){
        document.querySelector(".horizontal-scroll-bar").scrollLeft += 200;
    })

    const mrt_items = document.querySelectorAll(".horizontal-scroll-bar > .mrt-item");
    for (mrt_station of mrt_items){
        mrt_station.addEventListener("click",function(event){
            console.log(`Clicked on MRT: ${this.textContent}`); // this的用法
            keyword_document = this.textContent;
            document.querySelector("#attraction_search_query").value = this.textContent;
            searchAttraction(keyword_document);
        })
    }
}

// 初始化無限捲動(infinite scroll)IntersectionObserver
function initializeObserver(){
    let options = {
        root: null,
        rootMargin: "0px",
        threshold: 0,
        delay: 500
    };
    let callback = ((entries) =>{
        entries.forEach(entry => {
            if (entry.isIntersecting){
                // console.log(entry);
                console.log("Intersection Observed, Loading more...");
                loadMoreDataAndAddToDOM();
            }
        })
    })

    let observer = new IntersectionObserver(callback, options);
    let target = document.querySelector("#intersectionObserverObj");
    observer.observe(target);
}

// 初始化Search bar Event Listener
function initializeSearchBarListener(){
    const attraction_search_form = document.querySelector("#attraction_search_form");
    attraction_search_form.addEventListener("submit", function (event){
        event.preventDefault();
        keyword_document = document.querySelector("#attraction_search_query").value;
        searchAttraction(keyword_document);
    })
}

// 捲動到底後load more callback函數(infinite scroll)
async function loadMoreDataAndAddToDOM(){   
    console.log(nextPage);
    if (!nextPage){
        console.log("No more data.")
        return;
    }
    else {
    await fetchNewAttractions(page_input = nextPage, keyword_input = keyword_document);
    await createBigBox();
    await addAttractionData();
    }
}

// search bar相關函數clearAllBigBoxes, searchAttraction
// 清除畫面上所有attraction divs
function clearAllBigBoxes(){  
    const attractions_on_screen = document.querySelectorAll(".attraction") 
    for (attraction of attractions_on_screen){
        attraction.remove();
    }
    return;
}

// 關鍵字搜尋功能
async function searchAttraction(keyword){
    await fetchNewAttractions(page_input = 0, keyword_input = keyword);
    clearAllBigBoxes();
    await createBigBox();
    await addAttractionData();
}

// ***畫面初始化***
initializeJSON();
initializeHorizontalScroll();
initializeObserver();
initializeSearchBarListener();

