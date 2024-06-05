const bigBoxQty = 12;
let nextPage = null;
let keyword_document = null;
let initial_json;
let current_page = 0;
const attractions_per_load = 12;
let items_in_response;

async function fetchNewAttractions(page_input, keyword_input = null){
    current_page = page_input;
    
    let params = new URLSearchParams({page: page_input});
    if (keyword_input){
        params.append('keyword', keyword_input)
    }
    let url = "api/attractions?" + params;
    console.log(`Params: ${params}`);
    console.log(`Fetching url: ${url}`);
    const response = await fetch(url);
    const response_json = await response.json();
    console.log("Fetch response:");
    console.log(response_json);
    nextPage = response_json.nextPage;
    console.log(`nextPage no. from local: ${nextPage}`);
    items_in_response = response_json.data.length;
    console.log(`Items in response: ${items_in_response}`);
    initial_json = response_json;
    return response_json;
}

function createBigBox(){
    for (let box=0;box<(items_in_response);box++){
        const bigBoxGroup = document.querySelector(".bigboxgroup");
        const newBox = document.createElement("div");
        newBox.className = "attraction";
        
        const newBoxImg = document.createElement("img");
        newBoxImg.src = "";
        newBoxImg.className = "bigboximage";
        newBox.appendChild(newBoxImg);

        const newTextBlock1 = document.createElement("div");
        newTextBlock1.className = "text-block-1";
        const newTextBlock1Text = document.createElement("div");
        newTextBlock1Text.className = "text-block-1-text";
        newTextBlock1Text.textContent = "";
        newTextBlock1.appendChild(newTextBlock1Text);
        newBox.appendChild(newTextBlock1);

        const newTextBlock2 = document.createElement("div");
        newTextBlock2.className = "text-block-2";
        const newTextBlock2Text = document.createElement("div");
        newTextBlock2Text.className = "text-block-2-text";
        newTextBlock2Text.textContent = "";
        newTextBlock2.appendChild(newTextBlock2Text);
        const newTextBlock3Text = document.createElement("div");
        newTextBlock3Text.className = "text-block-3-text";
        newTextBlock3Text.textContent = "";
        newTextBlock2.appendChild(newTextBlock3Text);
        newBox.appendChild(newTextBlock2);

        bigBoxGroup.appendChild(newBox);
    }
}

async function addData(){
    console.log("adding data");
    console.log(initial_json);
    console.log("current page:");
    console.log(current_page);

    for (let box=0;box<(items_in_response);box++){
        //render text
        let box_no = current_page * attractions_per_load + box;

        let block1Text = document.querySelectorAll(".text-block-1-text")[box_no];
        let block1TextNode = document.createTextNode(`${initial_json.data[box].name}`);
        block1Text.appendChild(block1TextNode);

        let block2Text = document.querySelectorAll(".text-block-2-text")[box_no];
        let block2TextNode = document.createTextNode(`${initial_json.data[box].mrt}`);
        block2Text.appendChild(block2TextNode);

        let block3Text = document.querySelectorAll(".text-block-3-text")[box_no];
        let block3TextNode = document.createTextNode(`${initial_json.data[box].category}`);
        block3Text.appendChild(block3TextNode);
        
        //render images
        let block1Img = document.querySelectorAll(".bigboximage")[box_no];
        const block1imgURL = initial_json.data[box].images[0];
        block1Img.src = block1imgURL;
    }

}

async function fetchInitialAttractions(){
    const response = await fetch("api/attractions?page=0");
    const response_json = await response.json();
    console.log(`nextPage no. from response: ${response_json.nextPage}`);
    nextPage = response_json.nextPage;
    console.log(`nextPage no. from local: ${nextPage}`);
    items_in_response = response_json.data.length;
    console.log(`Items in response: ${items_in_response}`);
    console.log(response_json);
    return response_json;
};

async function initializeJSON(){
    await fetchNewAttractions(page_input = 0, keyword_input = null);
    // initial_json = await fetchInitialAttractions();
    console.log(initial_json);
    addData();
    return initial_json;
}

async function loadMoreData(){    
    console.log(initial_json);
    const new_json = await fetchNewAttractions(page_input=initial_json.nextPage,keyword_input=keyword_document);
    console.log(new_json);
    initial_json = new_json;
    console.log("loaded more!");
}

async function loadMoreDataAndAddToDOM(){   
    console.log(nextPage);
    if (!nextPage){
        console.log("No more data.")
        return;
    }
    else {
    await fetchNewAttractions(page_input = nextPage, keyword_input = keyword_document);
    await createBigBox();
    await addData();
    }
}

function clearAllBigBoxes(){  
    const attractions_on_screen = document.querySelectorAll(".attraction") 
    for (attraction of attractions_on_screen){
        attraction.remove();
    }
    return;
}

function initializeObserver(){
    let options = {
        root: null,
        rootMargin: "0px",
        threshold: 0,
        delay:1000
    };
    let callback = ((entries) =>{
        entries.forEach(entry => {
            if (entry.isIntersecting){
                console.log(entry);
                loadMoreDataAndAddToDOM();
            }
        })
    })

    let observer = new IntersectionObserver(callback, options);
    let target = document.querySelector("#intersectionObserverObj");
    observer.observe(target);
}

const attraction_search_form = document.querySelector("#attraction_search_form");
attraction_search_form.addEventListener("submit", function (event){
    event.preventDefault();
    keyword_document = document.querySelector("#attraction_search_query").value;
    searchAttraction(keyword_document);
})

async function searchAttraction(keyword){
    // keyword_document = document.querySelector("#attraction_search_query").value;
    await fetchNewAttractions(page_input = 0, keyword_input = keyword);
    clearAllBigBoxes();
    await createBigBox();
    await addData();
}

// 初始化
initializeJSON();
initializeObserver();
initializeHorizontalScroll();

//橫向卷軸功能與初始化
async function initializeHorizontalScroll(){
    const response = await fetch("api/mrts");
    const response_json = await response.json();
    mrt_stations = response_json.data.length;
    console.log(response_json);
    console.log(mrt_stations);

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
        console.log("Scrolled left!");
    })

    const horizontal_scrollbar_right = document.querySelector("#scroll-right");
    horizontal_scrollbar_right.addEventListener("click", function (event){
        document.querySelector(".horizontal-scroll-bar").scrollLeft += 200;
        console.log("Scrolled right!");
    })

    const mrt_items = document.querySelectorAll(".horizontal-scroll-bar > .mrt-item");
    for (mrt_station of mrt_items){
        mrt_station.addEventListener("click",function(event){
            console.log(this.textContent); // this的力量
            keyword_document = this.textContent;
            document.querySelector("#attraction_search_query").value = this.textContent;
            searchAttraction(keyword_document);
        })
    }
}