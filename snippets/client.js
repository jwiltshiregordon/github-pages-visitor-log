logVisitorMessage("Someone visited my github pages website!");

function logVisitorMessage(event_details) {
  const repoOwner = "REPO_OWNER";
  const repoName = "REPO_NAME";

  const data = {
    repo_owner: repoOwner,
    repo_name: repoName,
    event_details: event_details
  };

  fetch('https://api.github-pages-visitor-log.net/log', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      console.log('Message logged successfully:', data);
    } else {
      console.error('Error logging message:', data);
    }
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}

