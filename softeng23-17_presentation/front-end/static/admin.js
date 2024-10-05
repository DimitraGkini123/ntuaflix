function toggleSearchBar() {
    const searchBar = document.getElementById('searchBar');
    searchBar.style.transform = (searchBar.style.transform === 'scaleX(0)' || searchBar.style.transform === '') ? 'scaleX(1)' : 'scaleX(0)';
}

function closeSearchBar() {
    const searchBar = document.getElementById('searchBar');
    searchBar.style.transform = 'scaleX(0)';
}

function performHealthCheck() {
    // Make an AJAX request to the /admin/healthcheck endpoint
    fetch('/ntuaflix_api/admin/healthcheck')
        .then(response => response.json())
        .then(result => {
            // Display the result in the resultContainer div
            document.getElementById('resultContainer').innerHTML = JSON.stringify(result, null, 2);

            // Check the status and display a message
            if (result.status === 'OK') {
                showMessage('Health check passed!');
            } else {
                showMessage('Health check failed. Check the console for details.');
            }
        })
        .catch(error => {
            console.error('Error performing health check:', error);
            showMessage('Error performing health check. Check the console for details.');
        });
}

function showMessage(message) {
    // Display a message below the resultContainer div
    var messageElement = document.createElement('p');
    messageElement.innerText = message;
    document.getElementById('resultContainer').appendChild(messageElement);
}

//R E S E T  A L L 
document.getElementById('resetButton').addEventListener('click', function () {
    resetAll();
});

function resetAll() {
    // Make an AJAX request to the /admin/resetall endpoint
    fetch('/ntuaflix_api/admin/resetall', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(result => {
            console.log(result);
            if (result.status === 'OK') {
                showMessage('Everything Deleted!');
            } else {
                showMessage('Delete Failed! Check the console for details.');
            }
        })
        .catch(error => { console.error('Error resetting data:', error); });
}

// Upload title_basics
function uploadTitleBasics() {
    // Trigger file input click
    document.getElementById('fileInputBasics').click();
}

// Handle file selection
document.getElementById('fileInputBasics').addEventListener('change', function () {
    // Get the selected file
    const file = this.files[0];

    // Create a FormData object and append the file
    const formData = new FormData();
    formData.append('file', file);

    // Use fetch to send the FormData to the server
    fetch('/ntuaflix_api/admin/upload/titlebasics', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(data.message || data.error);
        })
        .catch(error => {
            console.error(error);
            alert('An error occurred while uploading the file.');
        });
});

// Upload title_akas
function uploadTitleAkas() {
    document.getElementById('fileInputAkas').click();
}

document.getElementById('fileInputAkas').addEventListener('change', function () {
    const file = this.files[0];

    const formData = new FormData();
    formData.append('file', file);

    fetch('/ntuaflix_api/admin/upload/titleakas', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(data.message || data.error);
        })
        .catch(error => {
            console.error(error);
            alert('An error occurred while uploading the file.');
        });
});

//Upload name_basics
function uploadNameBasics() {
    document.getElementById('fileInputNameBasics').click();
}
document.getElementById('fileInputNameBasics').addEventListener('change', function () {
    const file = this.files[0];

    const formData = new FormData();
    formData.append('file', file);

    fetch('/ntuaflix_api/admin/upload/namebasics', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(data.message || data.error);
        })
        .catch(error => {
            console.error(error);
            alert('An error occurred while uploading the file.');
        });
});

//Upload Titlte Principles
function uploadTitlePrinciples() {
    document.getElementById('fileInputTitlePrinciples').click();
}
document.getElementById('fileInputTitlePrinciples').addEventListener('change', function () {
    const file = this.files[0];

    const formData = new FormData();
    formData.append('file', file);

    fetch('/ntuaflix_api/admin/upload/titleprincipals', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(data.message || data.error);
        })
        .catch(error => {
            console.error(error);
            alert('An error occurred while uploading the file.');
        });
});


// Upload title_crew
function uploadTitleCrew() {
    document.getElementById('fileInputCrew').click();
}

document.getElementById('fileInputCrew').addEventListener('change', function () {
    const file = this.files[0];

    const formData = new FormData();
    formData.append('file', file);

    fetch('/ntuaflix_api/admin/upload/titlecrew', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(data.message || data.error);
        })
        .catch(error => {
            console.error(error);
            alert('An error occurred while uploading the file.');
        });
});

// Upload title_episode
function uploadTitleEpisode() {
    document.getElementById('fileInputEpisode').click();
}

document.getElementById('fileInputEpisode').addEventListener('change', function () {
    const file = this.files[0];

    const formData = new FormData();
    formData.append('file', file);

    fetch('/ntuaflix_api/admin/upload/titleepisode', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(data.message || data.error);
        })
        .catch(error => {
            console.error(error);
            alert('An error occurred while uploading the file.');
        });
});

// Upload title_ratings
function uploadTitleRatings() {
    document.getElementById('fileInputRatings').click();
}

document.getElementById('fileInputRatings').addEventListener('change', function () {
    const file = this.files[0];

    const formData = new FormData();
    formData.append('file', file);

    fetch('/ntuaflix_api/admin/upload/titleratings', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(data.message || data.error);
        })
        .catch(error => {
            console.error(error);
            alert('An error occurred while uploading the file.');
        });
});

// Function to open the modal
function openUserModificationModal() {
    document.getElementById("userModificationModal").style.display = "flex";
}

// Function to close the modal
function closeUserModificationModal() {
    document.getElementById("userModificationModal").style.display = "none";
}

function submitForm() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    if (username === '' || password === '') {
        alert("Username and password are required fields.");
    }
    // Perform AJAX request to Flask route
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/ntuaflix_api/admin/usermod/" + username + "/" + password, true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                alert("User modification successful!");
            } else {
                alert("Error: " + xhr.responseText);
            }
        }
    };
    xhr.send();
}

function openUserInfoModal() {
    document.getElementById("userInfoModal").style.display = "flex";
}

function closeUserInfoModal() {
    document.getElementById("userInfoModal").style.display = "none";
}
function getInfo() {
    var username = document.getElementById("user").value;

    if (username === '') {
        alert("Username is required.");
        return;
    }

    // Perform AJAX request to Flask route using POST method
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/ntuaflix_api/admin/users/" + username, true);
    xhr.setRequestHeader("Content-Type", "application/json");

    // Send the username in the request body
    var requestBody = JSON.stringify({ username: username });
    xhr.send(requestBody);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                // Handle the successful response here
                var responseData = JSON.parse(xhr.responseText);
                alert("User information retrieved successfully: " + JSON.stringify(responseData));
            } else {
                // Handle the error response here
                alert("Error: " + xhr.responseText);
            }
        }
    };
    console.log("Username sent to backend:", username);
}

