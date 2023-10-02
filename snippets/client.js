
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

function formatLogsForDisplay(logs) {
  let formattedLogs = [];
  logs.forEach(log => {
    let details = log.event_details.split('\n').join('\t');
    let timeAgo = moment.utc(log.timestamp).fromNow();
    formattedLogs.push(`${timeAgo.padEnd(22, ' ')}${details}`);
  });
  return formattedLogs.join('\n');
}

function writeLogsToElement(logsElementId = "github-pages-log-element", repoOwner = "REPO_OWNER", repoName = "REPO_NAME") {
  const apiUrlBase = 'https://api.github-pages-visitor-log.net';
  document.getElementById(logsElementId).textContent = "loading...";
  new Promise(resolve => setTimeout(resolve, 1500))
  .then(() => fetch(apiUrlBase + '/fetch-logs?repo_owner=' + repoOwner + '&repo_name=' + repoName))
  .then(response => response.json())
  .then(data => {
      document.getElementById(logsElementId).textContent = formatLogsForDisplay(data.logs);
  });
}
