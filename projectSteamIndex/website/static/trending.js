// Add this to trending.js
function openTrendingPanel(type) {
    document.getElementById("trendingPanel").style.right = "0";
    document.getElementById("trendingPanel").style.width = "300px";
    if (type === 'trending') {
        document.getElementById("panelTitle").innerHTML = "&#x1F525; Targets";
        loadTrendingPlayers();
    } else {
        document.getElementById("panelTitle").innerHTML = "&#x2744; Fades";
        loadNotTrendingPlayers();
    }
    highlightActiveTab(type);
}

function closeTrendingPanel() {
    document.getElementById("trendingPanel").style.right = "-300px";
    removeActiveTabHighlight();
}

function toggleTrendingPanel(type) {
    if (document.getElementById("trendingPanel").style.right === "0px") {
        if (document.getElementById("panelTitle").innerText.includes(type === 'trending' ? "Targets" : "Fades")) {
            closeTrendingPanel();
        } else {
            openTrendingPanel(type);
        }
    } else {
        openTrendingPanel(type);
    }
}

function highlightActiveTab(type) {
    document.querySelector(".tab.firebtn").classList.remove("active");
    document.querySelector(".tab.icebtn").classList.remove("active");
    if (type === 'trending') {
        document.querySelector(".tab.firebtn").classList.add("active");
    } else {
        document.querySelector(".tab.icebtn").classList.add("active");
    }
}

function removeActiveTabHighlight() {
    document.querySelector(".tab.firebtn").classList.remove("active");
    document.querySelector(".tab.icebtn").classList.remove("active");
}

// Populate trending players (adjust as needed to fetch and display data)
function loadTrendingPlayers() {
    fetch('/get-trending-players', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            const trendingPlayersList = document.getElementById('trendingPlayersList');
            trendingPlayersList.innerHTML = '';
            data.forEach(player => {
                const listItem = document.createElement('li');
                const sentiment = parseFloat(player.sentiment);
                // Create span elements for name and sentiment
                const nameSpan = document.createElement('span');
                const sentimentSpan = document.createElement('span');
                // Style for floating left and right
                nameSpan.style.float = 'left';
                sentimentSpan.style.float = 'right';
                let totalNews = player.quote_count + player.report_count;
                // Populate text content
                nameSpan.textContent = "(" + totalNews + ") " + player.name;
                sentimentSpan.textContent = "(" + player.position + ") " + sentiment.toFixed(2);
                // Append spans to the list item
                listItem.appendChild(nameSpan);
                listItem.appendChild(sentimentSpan);
                // Add clearfix to clear floats
                listItem.style.clear = 'both';
                // listItem.textContent = player.name + ': ' + sentiment.toFixed(2);
                listItem.style.borderBottom = '1px solid #fff'; // Adjust color and thickness as needed
                trendingPlayersList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Populate not trending players (adjust as needed to fetch and display data)
function loadNotTrendingPlayers() {
    fetch('/get-not-trending-players', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            const trendingPlayersList = document.getElementById('trendingPlayersList');
            trendingPlayersList.innerHTML = '';
            data.forEach(player => {
                const listItem = document.createElement('li');
                const sentiment = parseFloat(player.sentiment);
                // Create span elements for name and sentiment
                const nameSpan = document.createElement('span');
                const sentimentSpan = document.createElement('span');
                // Style for floating left and right
                nameSpan.style.float = 'left';
                sentimentSpan.style.float = 'right';
                let totalNews = player.quote_count + player.report_count;
                // Populate text content
                nameSpan.textContent = "(" + totalNews + ") " + player.name;
                sentimentSpan.textContent = "(" + player.position + ") " + sentiment.toFixed(2);
                // Append spans to the list item
                listItem.appendChild(nameSpan);
                listItem.appendChild(sentimentSpan);
                // Add clearfix to clear floats
                listItem.style.clear = 'both';
                // listItem.textContent = player.name + ': ' + sentiment.toFixed(2);
                listItem.style.borderBottom = '1px solid #fff'; // Adjust color and thickness as needed
                trendingPlayersList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error:', error));
}

