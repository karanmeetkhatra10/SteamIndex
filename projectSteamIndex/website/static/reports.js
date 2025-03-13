document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch all player names and populate datalist
    const fetchAllPlayerNames = () => {
        fetch('/get_all_players')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch player names');
            }
            return response.json();
    })
        .then(names => {
            const datalist = document.getElementById('playerNameSuggestions');
            datalist.innerHTML = '';  // Clear previous suggestions

            // Display all player names in the datalist
            names.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            datalist.appendChild(option);
        });
    })
        .catch(error => console.error('Error fetching player names:', error));
};
    // Function to handle adding new report sections
    const setupDynamicReportSections = () => {
        let addReportBtn = document.getElementById('addReportBtn');
        addReportBtn.addEventListener('click', function() {
        let reportSection = document.querySelector('.report-section');
        let newSection = reportSection.cloneNode(true);  // Clone the first report section
        let form = document.getElementById('reportForm');
        setupDeleteButton(newSection);  // Setup delete button for cloned section
        resetFormInputs(newSection);  // Reset cloned inputs
        form.querySelector('#reportSections').appendChild(newSection);  // Append the cloned section
        });

        function resetFormInputs(section) {
            let inputs = section.querySelectorAll('input, textarea');
            inputs.forEach(function(input) {
            input.value = '';  // Clear input fields
        });
    }

        function setupDeleteButton(section) {
            let deleteBtn = section.querySelector('.delete-report-btn');
            deleteBtn.addEventListener('click', function() {
                section.remove();  // Remove the section from the DOM
    });
    }
};

    // Function to handle resetting all form fields
    const resetAllFields = () => {
        let inputs = document.querySelectorAll('input, textarea');
        inputs.forEach(function(input) {
            input.value = '';  // Clear input fields
    });
};

    // Call functions to fetch player names, set up report sections, and handle reset button
    fetchAllPlayerNames();
    setupDynamicReportSections();

    // Autocomplete functionality for player name input
    const input = document.getElementById('playerName');
    input.addEventListener('input', function() {
        const inputValue = this.value.trim().toLowerCase();
        // Additional autocomplete logic here if needed
});

    // Event listener for reset all fields button
    let resetAllFieldsBtn = document.getElementById('resetAllFieldsBtn');
    resetAllFieldsBtn.addEventListener('click', function() {
        resetAllFields();  // Call the reset function to clear all fields
});
});

