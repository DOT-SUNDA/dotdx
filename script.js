let ipList = [];
let onlineCount = 0;

async function loadIPAddresses() {
    try {
        const response = await fetch('ip.txt');
        if (!response.ok) {
            throw new Error('Failed to fetch IP addresses');
        }
        const ips = await response.text();
        ipList = ips.split('\n').map(ip => ip.trim()).filter(ip => ip);

        const container = document.getElementById('rdpContainer');
        ipList.forEach((ip, index) => {
            const box = document.createElement('div');
            box.className = 'box';

            const title = document.createElement('h2');
            title.textContent = `RDP ${String(index + 1).padStart(2, '0')}`;

            const statusText = document.createElement('p');
            statusText.className = 'status-text';
            statusText.id = `status-${index}`;
            statusText.textContent = 'Status: Unknown';

            const startButton = document.createElement('button');
            startButton.className = 'button start';
            startButton.textContent = 'Start';
            startButton.onclick = () => sendRequest(ip, '/start', index);

            const stopButton = document.createElement('button');
            stopButton.className = 'button stop';
            stopButton.textContent = 'Stop';
            stopButton.onclick = () => sendRequest(ip, '/stop', index);

            const restartButton = document.createElement('button');
            restartButton.className = 'button restart';
            restartButton.textContent = 'Restart';
            restartButton.onclick = () => sendRequest(ip, '/restart', index);

            box.appendChild(title);
            box.appendChild(startButton);
            box.appendChild(stopButton);
            box.appendChild(restartButton);
            box.appendChild(statusText);

            container.appendChild(box);

            // Fetch and update status for each IP
            fetchStatus(ip, index);
        });

        // Update total RDP count
        updateTotalRDPStatus(ipList.length, onlineCount);
    } catch (error) {
        document.getElementById('status').innerText = `Status: Error - ${error.message}`;
    }
}

function updateTotalRDPStatus(total, online) {
    const statusDiv = document.getElementById('status');
    statusDiv.innerText = `Total RDP: ${total}, Online: ${online}`;
}

async function fetchStatus(ip, index) {
    try {
        document.getElementById(`status-${index}`).textContent = 'Status: Checking...';

        const url = `http://${ip}:5000/status`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch status');
        }
        const data = await response.json();
        if (data.status === "success") {
            const apiStatus = data.api_status || "unknown";
            const seleniumStatus = data.selenium_status || "unknown";
            document.getElementById(`status-${index}`).textContent = `API: ${apiStatus}, Selenium: ${seleniumStatus}`;

            // Check if the RDP is online
            if (apiStatus === "online" || seleniumStatus === "online") {
                onlineCount++;
            }
        } else {
            document.getElementById(`status-${index}`).textContent = 'Status: Unavailable';
        }
    } catch (error) {
        document.getElementById(`status-${index}`).textContent = 'Status: Error';
    } finally {
        // Update total status after each fetch
        updateTotalRDPStatus(ipList.length, onlineCount);
    }
}

async function sendRequest(ip, endpoint, index) {
    try {
        document.getElementById(`status-${index}`).textContent = 'Status: Please wait...';

        const url = `http://${ip}:5000${endpoint}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Request failed');
        }
        const data = await response.text();
        document.getElementById('status').innerText = `Status: ${data}`;

        fetchStatus(ip, index);
    } catch (error) {
        document.getElementById('status').innerText = `Status: Error - ${error.message}`;
    }
}

async function sendBulkRequest(endpoint) {
    const statusDiv = document.getElementById('status');
    statusDiv.innerText = 'Status: Sending requests...';

    const promises = ipList.map(async (ip, index) => {
        try {
            const url = `http://${ip}:5000${endpoint}`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Failed for ${ip}`);
            }
            fetchStatus(ip, index);
            return `Success for ${ip}`;
        } catch (error) {
            return `Error for ${ip}: ${error.message}`;
        }
    });

    const results = await Promise.all(promises);
    statusDiv.innerText = `Status:\n${results.join('\n')}`;
}

// Load IP addresses when the page loads
document.addEventListener('DOMContentLoaded', loadIPAddresses);
