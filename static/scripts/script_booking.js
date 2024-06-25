function renderBookingData(bookingStatusJson){
    //有種可以簡化為神秘迴圈的感覺

    console.log("Rendering booking data...");
    if (!bookingStatusJson.data){
        // alert("Fetched data says there is no booking!!!!!");        
        const bookingMainContainer = document.querySelector(".booking-main-container");
        const noBookingText = document.createElement("div");
        noBookingText.classList = "booking-data-container body gray-70";
        noBookingText.textContent = "目前沒有任何待預訂的行程";
        const bookingForm = document.querySelector("#booking-form-id");
        bookingMainContainer.insertBefore(noBookingText, bookingForm);
        return false;
    }
    else{
        const bookingMainContainer = document.querySelector(".booking-main-container");
        const bookingAttractionContainer = document.createElement("div");
        bookingAttractionContainer.classList = "booking-attraction-container";
        // bookingMainContainer.appendChild(bookingAttractionContainer);
        
        const bookingForm = document.querySelector("#booking-form-id");
        bookingMainContainer.insertBefore(bookingAttractionContainer, bookingForm);

        // navbarElement = document.querySelector(".navbar-background")
        // bodyElement = document.querySelector("body")
        // bodyElement.insertBefore()
        // bookingMainContainer.appendChild();

        //image
        const bookingAttractionImageContainer = document.createElement("div");
        bookingAttractionImageContainer.classList = "booking-attraction-image-container";
        const bookingAttractionImage = document.createElement("img");
        bookingAttractionImage.classList = "booking-attraction-image";
        // TODO: dynamically render image!!! NOT YET TESTED
        bookingAttractionImage.src = bookingStatusJson.data.attraction.image;
        bookingAttractionImageContainer.appendChild(bookingAttractionImage);
        bookingAttractionContainer.appendChild(bookingAttractionImageContainer);

        // text div
        const bookingAttractionText = document.createElement("div");
        bookingAttractionText.classList = "booking-attraction-text";
        bookingAttractionContainer.appendChild(bookingAttractionText);

        // attraction name
        const bookingAttractionTextAttractionOuter = document.createElement("div");
        bookingAttractionTextAttractionOuter.classList = "body bold cyan-70";
        bookingAttractionTextAttractionOuter.textContent = "台北一日遊：";
        const bookingAttractionTextAttractionInner = document.createElement("span");
        bookingAttractionTextAttractionInner.classList = "booking-attraction-content body";
        bookingAttractionTextAttractionInner.id = "booking-name";
        bookingAttractionTextAttractionInner.textContent = bookingStatusJson.data.attraction.name;

        // attraction date
        const bookingAttractionTextDateOuter = document.createElement("div");
        bookingAttractionTextDateOuter.classList = "body bold gray-70";
        bookingAttractionTextDateOuter.textContent = "日期：";
        const bookingAttractionTextDateInner = document.createElement("span");
        bookingAttractionTextDateInner.classList = "booking-attraction-content body";
        bookingAttractionTextDateInner.id = "booking-date";
        bookingAttractionTextDateInner.textContent = bookingStatusJson.data.date;

        // attraction time
        const bookingAttractionTextTimeOuter = document.createElement("div");
        bookingAttractionTextTimeOuter.classList = "body bold gray-70";
        bookingAttractionTextTimeOuter.textContent = "時間：";
        const bookingAttractionTextTimeInner = document.createElement("span");
        bookingAttractionTextTimeInner.classList = "booking-attraction-content body";
        bookingAttractionTextTimeInner.id = "booking-time";
        bookingAttractionTextTimeInner.textContent = bookingStatusJson.data.time;

        // attraction price
        const  bookingAttractionTextPriceOuter = document.createElement("div");
        bookingAttractionTextPriceOuter.classList = "body bold gray-70";
        bookingAttractionTextPriceOuter.textContent = "費用：";
        const bookingAttractionTextPriceInner = document.createElement("span");
        bookingAttractionTextPriceInner.classList = "booking-attraction-content body";
        bookingAttractionTextPriceInner.id = "booking-price";
        bookingAttractionTextPriceInner.textContent = bookingStatusJson.data.price;

        // attraction address
        const bookingAttractionTextAddressOuter = document.createElement("div");
        bookingAttractionTextAddressOuter.classList = "body bold gray-70";
        bookingAttractionTextAddressOuter.textContent = "地點：";
        const bookingAttractionTextAddressInner = document.createElement("span");
        bookingAttractionTextAddressInner.classList = "booking-attraction-content body";
        bookingAttractionTextAddressInner.id = "booking-address";
        bookingAttractionTextAddressInner.textContent = bookingStatusJson.data.attraction.address;

        // append all newly created divs
        bookingAttractionText.appendChild(bookingAttractionTextAttractionOuter);
        bookingAttractionText.appendChild(bookingAttractionTextDateOuter);
        bookingAttractionText.appendChild(bookingAttractionTextTimeOuter);
        bookingAttractionText.appendChild(bookingAttractionTextPriceOuter);
        bookingAttractionText.appendChild(bookingAttractionTextAddressOuter);

        // append inner spans to outer divs
        bookingAttractionTextAttractionOuter.appendChild(bookingAttractionTextAttractionInner);
        bookingAttractionTextDateOuter.appendChild(bookingAttractionTextDateInner);
        bookingAttractionTextTimeOuter.appendChild(bookingAttractionTextTimeInner);
        bookingAttractionTextPriceOuter.appendChild(bookingAttractionTextPriceInner);
        bookingAttractionTextAddressOuter.appendChild(bookingAttractionTextAddressInner);

        // append delete button
        const bookingAttractionDeleteIconContainer = document.createElement("button");
        bookingAttractionDeleteIconContainer.classList = "booking-attraction-delete-icon";
        const bookingAttractionDeleteIcon = document.createElement("img");
        bookingAttractionDeleteIcon.src = "../static/images/delete.png";
        bookingAttractionDeleteIconContainer.appendChild(bookingAttractionDeleteIcon);
        bookingAttractionDeleteIconContainer.addEventListener("click", deleteBooking);

        bookingAttractionContainer.appendChild(bookingAttractionDeleteIconContainer);
        return true;
    }
}

function togglePaymentInput(){
    document.querySelector("#booking-form-id").style.display = "block";
    return;
}

// get signed in user data
async function initializeSignedInUserData(){
    signinData = await checkToken();
    if (signinData){     
        document.querySelector("#booking-name").textContent = signinData.name;
        bookingStatusJson = await fetchBookingApi();
        
        const renderResult = renderBookingData(bookingStatusJson);
        if (renderResult){
            togglePaymentInput();
        }
    }
    else{
        alert("Signed out!");
        window.location.pathname = "/";
    } 
}

initializeSignedInUserData();

// fetch booking API
async function fetchBookingApi(){
    let signinStatusToken = window.localStorage.getItem('token');
    bookingStatus = await fetch("./api/booking",{
        method: "get",        
        headers: {Authorization: `Bearer ${signinStatusToken}`}
    });
    bookingStatusJson = await bookingStatus.json();
    console.log(bookingStatusJson);
    return bookingStatusJson;
}

// fetch deleteBooking API
async function deleteBooking(){
    let signinStatusToken = window.localStorage.getItem('token');
    deleteStatus = await fetch("./api/booking",{
        method: "delete",        
        headers: {Authorization: `Bearer ${signinStatusToken}`}
    });
    deleteStatusJson = await deleteStatus.json();
    console.log(deleteStatusJson);
    if (deleteStatusJson.error){
        console.log("Delete unsuccessful, message:", deleteStatusJson.message);
        // add dynamic text here
    }
    else{        
        console.log("Delete successful! Refreshing in 3s...");
        // add dynamic text here
        setTimeout(() => window.location.reload(), 3000);
    }
    return deleteStatusJson;
}