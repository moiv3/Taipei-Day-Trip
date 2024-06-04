const bigBoxQty = 12;
let nextPage = null;
let initial_json = null;

async function fetchNewAttractions(page_input, keyword_input = null) {
    let url = "api/attractions?" + new URLSearchParams({
        page: page_input,
        keyword: keyword_input || undefined // Add the keyword only if it's not null
    });
    console.log(url);
    try {
        
        const response = await fetch(url);
        const response_json = await response.json();
        console.log(response_json);
        return response_json;
    } catch (error) {
        console.error("Error fetching new attractions:", error);
    }
}

async function fetchInitialAttractions() {
    try {
        const response = await fetch("api/attractions?page=0");
        const response_json = await response.json();
        console.log(response_json.nextPage);
        nextPage = response_json.nextPage;
        console.log(nextPage);
        if (nextPage) {
            document.querySelector('#loadMore').style.display = 'block';
        } else {
            document.querySelector('#loadMore').style.display = 'none';
        }

        for (let i = 0; i < bigBoxQty; i++) {
            // render text
            let block1Text = document.querySelectorAll(".text-block-1-text")[i];
            let block1TextNode = document.createTextNode(`${response_json.data[i].name}`);
            block1Text.appendChild(block1TextNode);

            let block2Text = document.querySelectorAll(".text-block-2-text")[i];
            let block2TextNode = document.createTextNode(`${response_json.data[i].mrt}`);
            block2Text.appendChild(block2TextNode);

            let block3Text = document.querySelectorAll(".text-block-3-text")[i];
            let block3TextNode = document.createTextNode(`${response_json.data[i].category}`);
            block3Text.appendChild(block3TextNode);

            // render images
            let block1Img = document.querySelectorAll(".bigboximage")[i];
            const block1imgURL = response_json.data[i].images[0];
            block1Img.src = block1imgURL;
        }

        console.log(response_json);
        return response_json;
    } catch (error) {
        console.error("Error fetching initial attractions:", error);
    }
}

async function initializeJSON() {
    initial_json = await fetchInitialAttractions();
    console.log(initial_json);
}

async function loadMore() {
    if (!initial_json) {
        console.error("Initial JSON is not set");
        return;
    }
    console.log(initial_json);
    await fetchNewAttractions(page_input = initial_json.nextPage, keyword_input = null);
    console.log("loaded more!");
}

initializeJSON();

document.querySelector('#loadMore').addEventListener('click', loadMore);