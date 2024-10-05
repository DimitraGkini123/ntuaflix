async function displayMovieResults(movie, movieContainer) {

    // Clear previous movie
    movieContainer.innerHTML = '';

    const titleContainer = document.createElement('div');
    titleContainer.classList.add('movieTitleContainer');
    const titleElement = document.createElement('h2'); // Using h2 for title
    titleElement.textContent = movie.originalTitle;
    titleContainer.appendChild(titleElement);

    const bigContainerElement = document.createElement('div');
    bigContainerElement.classList.add('bigContainer');

    const containerElement = document.createElement('div');
    containerElement.classList.add('mediumContainer');

    const posterSrc = movie.titlePoster ? movie.titlePoster : '/static/images/default.jpg';
    const posterElement = document.createElement('img');
    posterElement.src = await posterSrc.replace('{width_variable}', 'w500');
    posterElement.classList.add('row__poster2');

    bigContainerElement.appendChild(posterElement);

    const smallContainerElement = document.createElement('div');
    smallContainerElement.classList.add('smallContainer');
    // Create a div for movie information
    const movieInfoElement = document.createElement('div');
    movieInfoElement.classList.add('movieInfo2');

    const typeElement = document.createElement('p');
    typeElement.textContent = `Type: ${movie.type}`;
    movieInfoElement.appendChild(typeElement);

    const startYearElement = document.createElement('p');
    startYearElement.textContent = `Start Year: ${movie.startYear}`;
    movieInfoElement.appendChild(startYearElement);

    const genresElement = document.createElement('p');
    genresElement.textContent = `Genres: ${movie.genres.join(', ')}`;
    movieInfoElement.appendChild(genresElement);

    smallContainerElement.appendChild(movieInfoElement);

    // Ensure createListButton is defined
    const ratingContainer = document.createElement('div');
    ratingContainer.classList.add('ratingContainer');

    // ratingButtonContainer.insertBefore(starRating, ratingButtonContainer.firstChild);
    const ratingElement = document.createElement('h3');
    //ratingElement.textContent = `${movie.rating ? movie.rating.avRating : 'N/A'} (${movie.rating ? movie.rating.numVotes : '0'} votes)`;
    const avRating = movie.rating ? parseFloat(movie.rating.avRating).toFixed(3) : 'N/A';
    const numVotes = movie.rating ? movie.rating.numVotes : '0';
    ratingElement.textContent = `${avRating} (${numVotes} votes)`;
    
    // Create a container for the buttons
    const buttonsContainer = document.createElement('div');
    buttonsContainer.classList.add('buttonsContainer');

    async function createContent() {
        const likeButton = await createLikeButton(movie);
        const listButton = await createListButton(movie);

        buttonsContainer.appendChild(listButton);
        buttonsContainer.appendChild(likeButton);

        const yourRatingContainer = document.createElement('div');
        yourRatingContainer.classList.add('yourRatingContainer');
        // Create star rating container
        const starRatingContainer = document.createElement('div');
        starRatingContainer.className = 'star-rating';
        let selectedStars = 0;
        for (let i = 10; i >= 1; i--) {
            const starInput = document.createElement('input');
            starInput.type = 'radio';
            starInput.id = `star${i}`;
            starInput.name = 'rating';
            starInput.value = i;
        
            starInput.setAttribute('title', `${i} stars`);
        
            starInput.addEventListener('change', () => {
                selectedStars = parseInt(starInput.value);
                console.log('Selected stars:', selectedStars);
            });
        
            const starLabel = document.createElement('label');
            starLabel.htmlFor = `star${i}`;
            starLabel.title = `${i} stars`;
            starLabel.textContent = '★';
        
            starRatingContainer.appendChild(starInput);
            starRatingContainer.appendChild(starLabel);
        }
        // Create comment box container
        const commentBoxContainer = document.createElement('div');
        commentBoxContainer.classList.add('comment-box');

        const formElement = document.createElement('form');
        formElement.id = 'commentForm';

        const textareaElement = document.createElement('textarea');
        textareaElement.id = 'commentInput';
        textareaElement.placeholder = 'Add your comment here...';

        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = 'Submit';

        submitButton.addEventListener('click', async (event) => {
            event.preventDefault();
            if (selectedStars === 0) {
                alert('Please select your desired rating');
                return;
            }
            const commentInput = textareaElement.value;
        
            // Check if the user has already submitted a rating
            const response = await fetch(`/ntuaflix_api/check_rating/${movie.titleID}`);
            const data = await response.json();
        
            if (data.rated) {
                const confirmReplace = confirm('You have already reviewed this title. Do you want to replace your previous review?');
                if (!confirmReplace) {
                    return; // Stop if the user chooses not to replace
                }
                // User chooses to replace, call the replace_rating endpoint (to be implemented)
                await replaceRatingAndComment(movie.titleID, selectedStars, commentInput);
            } else {
                // User has not submitted a rating yet, proceed with sending the rating and comment
                console.log('selected stars are: ', selectedStars);
                await sendRatingAndComment(movie.titleID, selectedStars, commentInput);
            }
        });

        formElement.appendChild(textareaElement);
        formElement.appendChild(submitButton);

        commentBoxContainer.appendChild(formElement);

        // Append star rating and comment box containers to yourRatingContainer
        yourRatingContainer.appendChild(starRatingContainer);
        yourRatingContainer.appendChild(commentBoxContainer);

        // Append yourRatingContainer to the document or wherever you need it
        document.body.appendChild(yourRatingContainer);

        ratingContainer.appendChild(ratingElement);

        ratingContainer.appendChild(buttonsContainer);

        smallContainerElement.appendChild(ratingContainer);

        containerElement.appendChild(smallContainerElement);

        containerElement.appendChild(yourRatingContainer);

        bigContainerElement.appendChild(containerElement); 
    }
    await createContent();
    await movieContainer.appendChild(titleContainer);
    //movieContainer.appendChild(containerElement);
    await movieContainer.appendChild(bigContainerElement);

    await displayReviews(movie.titleID, movieContainer);
    
    async function sendRatingAndComment(movieId, ratingValue, comment) {
        const data = { rating: ratingValue, comment: comment };
        try {
            const response = await fetch(`/ntuaflix_api/rating/${movieId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
                
            });
            if (response.ok) {
                // Rating - comment submitted successfully
                console.log('Rating/comment submitted successfully');
                // Reload  UI if 
                window.location.reload();
            } else {
                // Error handling
                console.error('Error submitting rating or comment:', response.statusText);
            }
        } catch (error) {
            // Network error handling
            console.error('Network error:', error);
        }
    }

    async function replaceRatingAndComment(titleID, rating, comment) {
        try {
            const response = await fetch(`/ntuaflix_api/replace_rating/${titleID}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ rating, comment })
            });
    
            if (response.ok) {
                const data = await response.json();
                console.log(data.message); // Log success message
                window.location.reload();
            } else {
                const errorData = await response.json();
                console.error(errorData.error); // Log error message
            }
        } catch (error) {
            console.error('Network error:', error);
        }
    }
    

    async function displayReviews(movieId, movieContainer) {
        const reviewsContainer = document.createElement('div');
        reviewsContainer.classList.add('reviewsContainer');
        const reviewsTitle = document.createElement('h3');
        reviewsTitle.textContent = 'Reviews';
        reviewsContainer.appendChild(reviewsTitle);
    
        try {
            const response = await fetch(`/ntuaflix_api/movie_reviews/${movieId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch reviews');
            }
            const reviews = await response.json();
    
            if (reviews.length === 0) {
                const noReviewsMsg = document.createElement('p');
                noReviewsMsg.textContent = 'No reviews yet.';
                reviewsContainer.appendChild(noReviewsMsg);
            } else {
                reviews.forEach(review => {
                    const reviewElement = document.createElement('div');
                    reviewElement.classList.add('review');
    
                    const usernameElement = document.createElement('h4');
                    usernameElement.textContent = review.username;
    
                    const ratingElement = document.createElement('p');
                    ratingElement.textContent = `Rating: ${review.rating}`;
    
                    const commentElement = document.createElement('p');
                    commentElement.textContent = review.comment;
    
                    reviewElement.appendChild(usernameElement);
                    reviewElement.appendChild(ratingElement);
                    reviewElement.appendChild(commentElement);
    
                    reviewsContainer.appendChild(reviewElement);
                });
            }
        } catch (error) {
            console.error('Error loading reviews:', error);
            const errorMsg = document.createElement('p');
            errorMsg.textContent = 'Error loading reviews.';
            reviewsContainer.appendChild(errorMsg);
        }
    
        await movieContainer.appendChild(reviewsContainer);
    }
}