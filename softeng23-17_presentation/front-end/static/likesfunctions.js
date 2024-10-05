async function likelist(titleID) {
    try {
        const response = await fetch(`/ntuaflix_api/check_likelist/${titleID}`);
        const data = await response.json();
        return data.inLikelist;
    } catch (error) {
        console.error("Error checking Likelist:", error);
        return 0;
    }
}

async function createLikeButton(result) {
    const likeButton = document.createElement('button');
    movieInLikes = await likelist(result.titleID);
    likeButton.innerHTML = '&hearts;';
    likeButton.classList.add('likeButton');
    if (movieInLikes > 0){
        likeButton.classList.add('likeButton', 'full');
    }
    else{
        likeButton.classList.add('likeButton', 'empty');
    }
    likeButton.addEventListener('click', function () {
        toggleLike(result.titleID, likeButton);
    });
    return likeButton;
}


function toggleLike(titleID, button) {
// Toggle the like status and update the button appearance
if (button.classList.contains('empty')) {
    // If not liked, make it liked (full heart)
    button.classList.remove('empty');
    button.classList.add('full');
    // Call the function to handle the like operation
    addLike(titleID);
} else {
    // If already liked, make it not liked (empty heart)
    button.classList.remove('full');
    button.classList.add('empty');
    // Call the function to handle the unlike operation
    removeLike(titleID);
}
}
function addLike(titleID) {
    fetch('/ntuaflix_api/get_user_id')
        .then(response => response.json())
        .then(data => {
            const userID = data;
            console.log('User ID:', userID);

            if (!userID) {
                alert('Please log in to like movies');
                return;
            }

            fetch(`/ntuaflix_api/add_to_likes/${titleID}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ userID: userID }),
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        })
        .catch(error => {
            console.error('Error:', error);
        });    

}

function removeLike(titleID) {
    fetch('/ntuaflix_api/get_user_id')
        .then(response => response.json())
        .then(data => {
            const userID = data;
            console.log('User ID:', userID);

            if (!userID) {
                alert('Please log in to like movies');
                return;
            }

            fetch(`/ntuaflix_api/remove_from_likes/${titleID}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ userID: userID }),
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        })
        .catch(error => {
            console.error('Error:', error);
        });    

}