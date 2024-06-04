const bigBoxQty = 12;
let nextPage = null;
let keyword_document = null;
let initial_json;
let current_page = 0;
const attractions_per_load = 12;

async function fetchNewAttractions(page_input, keyword_input = null){
    current_page = page_input;
    
    let params = new URLSearchParams({page: page_input});
    if (keyword_input){
        params.append('keyword', keyword_input)
    }
    let url = "api/attractions?" + params;
    console.log(params);
    console.log(url);
    const response = await fetch(url);
    const response_json = await response.json();
    console.log(response_json);
    nextPage = response_json.nextPage;
    console.log(nextPage);
    return response_json;
}

function createBigBox(){
    for (let box=0;box<(attractions_per_load);box++){
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

    /*
    const response = await fetch("api/attractions?page=0");
    const response_json = await response.json();
    console.log(response_json.nextPage);
    nextPage = response_json.nextPage;
    console.log(nextPage);
    if (nextPage){
        document.querySelector('#loadMore').style.display='block';
    }
    else{
        document.querySelector('#loadMore').style.display='none';
    }
    */
    for (let box=0;box<(attractions_per_load);box++){
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
    console.log(response_json.nextPage);
    nextPage = response_json.nextPage;
    console.log(nextPage);
    if (nextPage){
        document.querySelector('#loadMore').style.display='block';
    }
    else{
        document.querySelector('#loadMore').style.display='none';
    }

    for (let i=0;i<(bigBoxQty);i++){
        //render text
        let block1Text = document.querySelectorAll(".text-block-1-text")[i];
        let block1TextNode = document.createTextNode(`${response_json.data[i].name}`);
        block1Text.appendChild(block1TextNode);

        let block2Text = document.querySelectorAll(".text-block-2-text")[i];
        let block2TextNode = document.createTextNode(`${response_json.data[i].mrt}`);
        block2Text.appendChild(block2TextNode);

        let block3Text = document.querySelectorAll(".text-block-3-text")[i];
        let block3TextNode = document.createTextNode(`${response_json.data[i].category}`);
        block3Text.appendChild(block3TextNode);
        
        //render images
        let block1Img = document.querySelectorAll(".bigboximage")[i];
        const block1imgURL = response_json.data[i].images[0];
        block1Img.src = block1imgURL;
    }

    console.log(response_json);
    return response_json;
};

async function initializeJSON(){
    initial_json = await fetchInitialAttractions();
    console.log(initial_json);
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
    await loadMoreData();
    await createBigBox();
    await addData();
    }
    // await Check();
}


initializeJSON();

// document.querySelector('#loadMore').addEventListener('click', loadMoreDataAndAddToDOM);
// document.querySelector('#createBigBox').addEventListener('click', createBigBox);
// document.querySelector('#addData').addEventListener('click', addData);

let options = {
    root: null,
    rootMargin: "0px",
    threshold: 0,
    delay:2000
  };
let callback = ((entries) =>{
    entries.forEach(entry => {
        if (entry.isIntersecting){
            console.log(entry);
            loadMoreDataAndAddToDOM();
            //observer.observe(target);
        }
    })
})
    // loadMoreDataAndAddToDOM());
let observer = new IntersectionObserver(callback, options);

// let attraction_array = document.querySelectorAll(".attraction");
// let target = document.querySelectorAll(".attraction")[attraction_array.length-1];

let target = document.querySelector("#intersectionObserverObj");
observer.observe(target);

