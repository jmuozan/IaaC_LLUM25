const transcriptionsContainer = document.getElementById("transcriptions");
const loadingElement = document.getElementById("loading");

let sentences = []; // Sentences will be dynamically loaded
let packageIndex = 0;

// Simulate fetching sentences from the server
function fetchSentences() {
    return fetch("/static/sentences.json")
        .then((response) => response.json())
        .then((data) => {
            sentences = data;
        });
}

// Display a package of 3 sentences as falling text
function displayPackage() {
    if (packageIndex >= sentences.length) {
        packageIndex = 0; // Restart the loop
    }

    const package = sentences.slice(packageIndex, packageIndex + 3);
    packageIndex += 3;

    transcriptionsContainer.innerHTML = ""; // Clear previous sentences
    package.forEach((sentence, index) => {
        const sentenceElement = document.createElement("div");
        sentenceElement.className = "sentence";
        sentenceElement.style.animationDelay = `${index * 1.5}s`; // Stagger animations
        sentenceElement.textContent = sentence;
        transcriptionsContainer.appendChild(sentenceElement);
    });
}

// Handle loading state
function showLoading() {
    loadingElement.style.display = "block";
}

function hideLoading() {
    loadingElement.style.display = "none";
}

// Initialize the app
async function initialize() {
    await fetchSentences(); // Load sentences
    hideLoading(); // Hide loading state
    displayPackage(); // Display the first package

    // Rotate packages every 10 seconds
    setInterval(() => {
        showLoading();
        setTimeout(() => {
            hideLoading();
            displayPackage();
        }, 2000); // Simulate loading delay
    }, 10000);
}

initialize();
