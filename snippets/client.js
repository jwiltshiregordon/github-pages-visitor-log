
const repoOwner = "REPO_OWNER";
const repoName = "REPO_NAME";

logVisitorMessage(`Someone visited my github pages website ${repoOwner}/${repoName}`);
writeLogsToElement();

function logVisitorMessage(event_details) {
  const apiUrlBase = 'https://api.github-pages-visitor-log.net';
  const data = {
    repo_owner: repoOwner,
    repo_name: repoName,
    event_details: event_details
  };

  fetch(apiUrlBase + '/log', {
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

function writeLogsToElement(logsElementId = "github-pages-log-element") {
  const apiUrlBase = 'https://api.github-pages-visitor-log.net';
  document.getElementById(logsElementId).textContent = "loading...";
  fetch(apiUrlBase + '/fetch-logs?repo_owner=' + repoOwner + '&repo_name=' + repoName)
  .then(response => response.json())
  .then(data => {
      document.getElementById(logsElementId).textContent = formatLogsForDisplay(data.logs);
  });
}
