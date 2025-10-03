document.addEventListener('DOMContentLoaded', () => {
    // === DOM Elements ===
    const urlInput = document.getElementById('url-input');
    const checkBtn = document.getElementById('check-btn');
    const resultSection = document.getElementById('result-section');
    const historySection = document.getElementById('history-section');
    const historyList = document.getElementById('history-list');
    const resultCardTemplate = document.getElementById('result-card-template');

    // === API Configuration ===
    const API_URL_ANALYZE = "http://localhost:8000/analyze";
    const API_URL_RESULTS = "http://localhost:8000/results";

    let pollingInterval;

    // === Event Listeners ===
    checkBtn.addEventListener('click', handleSubmit);
    urlInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            handleSubmit();
        }
    });

    // === Core Functions ===
    async function handleSubmit() {
        const url = urlInput.value.trim();
        if (!url || !url.startsWith('http')) {
            alert("Silakan masukkan URL yang valid (diawali dengan http:// atau https://).");
            return;
        }

        setLoadingState(true);
        displayResult({ status: 'PENDING', url: url });
        
        try {
            const response = await fetch(`${API_URL_ANALYZE}?url=${encodeURIComponent(url)}`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error("Gagal memulai analisis di server.");

            const data = await response.json();
            pollForResult(data.task_id, url); // Kirim URL untuk ditampilkan jika error

        } catch (error) {
            displayResult({ status: 'ERROR', url: url, error: error.message });
            setLoadingState(false);
        }
    }

    function pollForResult(taskId, url) {
        clearInterval(pollingInterval);

        pollingInterval = setInterval(async () => {
            try {
                const response = await fetch(API_URL_RESULTS, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task_ids: [taskId] })
                });

                if (!response.ok) throw new Error("Gagal mengambil hasil dari server.");

                const data = await response.json();
                const result = data[0];

                if (result && result.status === 'COMPLETE') {
                    clearInterval(pollingInterval);
                    setLoadingState(false);
                    displayResult(result);
                    addToHistory(result);
                } else if (!result || result.status === 'NOT_FOUND') {
                    // Terus mencoba jika belum ada
                }
            } catch (error) {
                clearInterval(pollingInterval);
                setLoadingState(false);
                displayResult({ status: 'ERROR', url: url, error: error.message });
            }
        }, 3000); // Periksa setiap 3 detik
    }

    // === UI Helper Functions ===
    function setLoadingState(isLoading) {
        checkBtn.disabled = isLoading;
        urlInput.disabled = isLoading;
        checkBtn.textContent = isLoading ? 'Menganalisis...' : 'Periksa';
    }

    function displayResult(result) {
        resultSection.innerHTML = '';
        
        const cardClone = resultCardTemplate.content.cloneNode(true);
        const verdictEl = cardClone.querySelector('.verdict');
        const urlEl = cardClone.querySelector('.url-checked');
        const reasonsListEl = cardClone.querySelector('.reasons-list');
        const resultCardEl = cardClone.querySelector('.result-card');

        urlEl.textContent = `URL Diperiksa: ${result.url}`;

        if (result.status === 'PENDING') {
            resultCardEl.classList.add('pending');
            verdictEl.textContent = '⏳ Sedang Dianalisis...';
            const li = document.createElement('li');
            li.textContent = "Proses scraping dan analisis AI sedang berjalan di background.";
            reasonsListEl.appendChild(li);
        } else if (result.status === 'COMPLETE') {
            if (result.is_suspicious) {
                resultCardEl.classList.add('suspicious');
                verdictEl.textContent = '❌ Berbahaya';
            } else {
                resultCardEl.classList.add('safe');
                verdictEl.textContent = '✅ Aman';
            }
            (result.reasons || [result.verdict]).forEach(reason => {
                const li = document.createElement('li');
                li.textContent = reason;
                reasonsListEl.appendChild(li);
            });
        } else { // ERROR
             resultCardEl.classList.add('suspicious');
             verdictEl.textContent = '🔌 Terjadi Error';
             const li = document.createElement('li');
             li.textContent = result.error || 'Tidak bisa terhubung ke server.';
             reasonsListEl.appendChild(li);
        }

        resultSection.classList.remove('hidden');
        resultSection.appendChild(cardClone);
    }

    function addToHistory(result) {
        const li = document.createElement('li');
        const icon = result.is_suspicious ? '❌' : '✅';
        li.innerHTML = `${icon} ${result.url}`;
        historyList.prepend(li);
        
        if (historyList.children.length > 5) {
            historyList.lastChild.remove();
        }
        historySection.classList.remove('hidden');
    }
});