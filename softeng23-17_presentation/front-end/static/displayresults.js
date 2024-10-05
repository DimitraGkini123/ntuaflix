async function displaySearchResults(results, resultsContainer) {
    // Clear previous results
    resultsContainer.innerHTML = '';

    if (results && results.length > 0) {
        // Loop through the results and create HTML elements to display them
        for (const result of results) {
            const resultElement = document.createElement('div');
            resultElement.classList.add('searchResult'); // Add a class for styling

            const posterSrc = result.titlePoster ? result.titlePoster : '/static/images/default.jpg';
            const posterElement = document.createElement('img');
            posterElement.src = posterSrc.replace('{width_variable}', 'w500');
            posterElement.classList.add('row__poster');
            resultElement.appendChild(posterElement);

            posterElement.addEventListener('click', () => {
                console.log(`Clicked poster for movie: ${result.originalTitle}`);
                window.location.href = `/ntuaflix_api/info/${result.titleID}`;
            });

            // Create a div for movie information
            const movieInfoElement = document.createElement('div');
            movieInfoElement.classList.add('movieInfo');

            // Add various details about the movie
            const titleElement = document.createElement('p');
            titleElement.textContent = `Title: ${result.originalTitle}`;
            movieInfoElement.appendChild(titleElement);

            const typeElement = document.createElement('p');
            typeElement.textContent = `Type: ${result.type}`;
            movieInfoElement.appendChild(typeElement);

            const startYearElement = document.createElement('p');
            startYearElement.textContent = `Start Year: ${result.startYear}`;
            movieInfoElement.appendChild(startYearElement);

            const genresElement = document.createElement('p');
            genresElement.textContent = `Genres: ${result.genres.join(', ')}`;
            movieInfoElement.appendChild(genresElement);

            const ratingElement = document.createElement('p');
            ratingElement.textContent = `Rating: ${result.rating ? result.rating.avRating : 'N/A'} (${result.rating ? result.rating.numVotes : '0'} votes)`;
            movieInfoElement.appendChild(ratingElement);

            resultElement.appendChild(movieInfoElement);

            // Ensure createListButton is defined
            const listButton = await createListButton(result);
            resultElement.appendChild(listButton);

            // Ensure createLikeButton is defined
            const likeButton = await createLikeButton(result);
            resultElement.appendChild(likeButton);

            // Append resultElement to resultsContainer
            resultsContainer.appendChild(resultElement);

            // Create and append a horizontal line between results
            const hrElement = document.createElement('hr');
            resultsContainer.appendChild(hrElement);

            console.log('listButton type:', typeof listButton, listButton);
            console.log('likeButton type:', typeof likeButton, likeButton);
            console.log('hrElement type:', typeof hrElement, hrElement);
        }
    } else {
        // Display a message for no results
        resultsContainer.innerHTML = '<p>No results found.</p>';
    }
}