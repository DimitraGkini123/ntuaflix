function displayprincipals(results, resultsContainer) {
    // Clear previous results
    resultsContainer.innerHTML = '';

    if (results && results.length > 0) {
        // Loop through the results and create HTML elements to display them
        results.forEach(result => {
            const resultElement = document.createElement('div');
            resultElement.classList.add('searchResult'); // Add a class for styling

            const posterSrc = result.namePoster ? result.namePoster : '/static/images/default_image_for_names.jpeg';
            const posterElement = document.createElement('img');
            posterElement.src = posterSrc.replace('{width_variable}', 'w500');
            posterElement.classList.add('row__poster');
            resultElement.appendChild(posterElement);

            // Create a div for movie information
            const nameInfoElement = document.createElement('div');
            nameInfoElement.classList.add('nameInfo');

            // Add various details about the movie
            const nameElement = document.createElement('p');
            nameElement.textContent = `Name: ${result.name}`;
            nameInfoElement.appendChild(nameElement);

            const birthYearElement = document.createElement('p');
            birthYearElement.textContent = `Birth Year: ${result.birthYr}`;
            nameInfoElement.appendChild(birthYearElement);

            const deathYearElement = document.createElement('p');
            deathYearElement.textContent = `Death Year: ${result.deathYr ? result.deathYr : 'N/A'}`;
            nameInfoElement.appendChild(deathYearElement);

            const professionElement = document.createElement('p');
            professionElement.textContent = `Profession: ${result.profession}`;
            nameInfoElement.appendChild(professionElement);

            // Check if there are nameTitles
            if (result.nameTitles && result.nameTitles.length > 0) {
                const titleListElement = document.createElement('ul');

                result.nameTitles.forEach(title => {
                    const titleListItem = document.createElement('li');
                    titleListItem.textContent = `Title ID: ${title.titleID}, Category: ${title.category}`;
                    titleListElement.appendChild(titleListItem);
                });

                nameInfoElement.appendChild(titleListElement);
            }

            // Append nameInfoElement to resultElement
            resultElement.appendChild(nameInfoElement);

            // Append resultElement to resultsContainer
            resultsContainer.appendChild(resultElement);

            // Add a horizontal line between results
            const hrElement = document.createElement('hr');
            resultsContainer.appendChild(hrElement);
        });

    } else {
        // Display a message for no results
        resultsContainer.innerHTML = '<p>No results found.</p>';
    }
}