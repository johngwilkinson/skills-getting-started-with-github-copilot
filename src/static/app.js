// Function to fetch activities from API
async function fetchActivities() {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  try {
    const response = await fetch("/activities");
    const activities = await response.json();

    // Clear loading message
    activitiesList.innerHTML = "";
    activitySelect.innerHTML = ""; // Clear previous options

    // Populate activities list
    Object.entries(activities).forEach(([name, details]) => {
      const activityCard = document.createElement("div");
      activityCard.className = "activity-card";

      const spotsLeft = details.max_participants - details.participants.length;
      const isFull = spotsLeft === 0;

      // Create participants list HTML
      let participantsHTML = '';
      if (details.participants.length > 0) {
        const participantsList = details.participants
          .map(email => `
            <li class="participant-item">
              <span>${email}</span>
              <span class="delete-icon" onclick="unregisterParticipant('${name}', '${email}')">×</span>
            </li>
          `).join('');
        participantsHTML = `
          <div class="participants-section">
            <div class="participants-header">
              <span class="participants-title">Participants</span>
              <span class="participants-count ${isFull ? 'full' : ''}">${details.participants.length}/${details.max_participants}</span>
            </div>
            <ul class="participants-list">${participantsList}</ul>
          </div>
        `;
      } else {
        participantsHTML = `
          <div class="participants-section">
            <div class="participants-header">
              <span class="participants-title">Participants</span>
              <span class="participants-count">${details.participants.length}/${details.max_participants}</span>
            </div>
            <div class="no-participants">No participants yet - be the first to join!</div>
          </div>
        `;
      }

      activityCard.innerHTML = `
        <h4>${name}</h4>
        <p class="activity-description">${details.description}</p>
        <p class="activity-schedule"><strong>Schedule:</strong> ${details.schedule}</p>
        <p class="activity-availability"><strong>Availability:</strong> ${spotsLeft} spots left</p>
        ${participantsHTML}
      `;

      if (isFull) {
        activityCard.classList.add('full-activity');
      }

      activitiesList.appendChild(activityCard);

      // Add option to select dropdown
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      activitySelect.appendChild(option);
    });
  } catch (error) {
    activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
    console.error("Error fetching activities:", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Refresh activities to show updated participants
      if (response.ok) {
        fetchActivities();
      }

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});

// Function to unregister a participant
async function unregisterParticipant(activityName, email) {
  if (!confirm(`Are you sure you want to unregister ${email} from ${activityName}?`)) {
    return;
  }

  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );

    const result = await response.json();

    if (response.ok) {
      // Refresh activities to show updated participants
      fetchActivities();
      
      // Show success message
      const messageDiv = document.getElementById("message");
      messageDiv.textContent = result.message;
      messageDiv.className = "success";
      messageDiv.classList.remove("hidden");

      // Hide message after 3 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 3000);
    } else {
      // Show error message
      const messageDiv = document.getElementById("message");
      messageDiv.textContent = result.detail || "Failed to unregister participant";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");

      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    }
  } catch (error) {
    // Show error message
    const messageDiv = document.getElementById("message");
    messageDiv.textContent = "Failed to unregister participant. Please try again.";
    messageDiv.className = "error";
    messageDiv.classList.remove("hidden");
    console.error("Error unregistering participant:", error);

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }
}
