// datatable.js

export class AjaxDataTable {
    constructor(options) {
        this.apiUrl = options.apiUrl;
        this.rowsPerPage = options.rowsPerPage || 10;
        this.currentPage = 1;
        this.total = 0;
        this.tableBody = document.getElementById(options.tableBodyId);
        this.prevBtn = document.getElementById(options.prevBtnId);
        this.nextBtn = document.getElementById(options.nextBtnId);
        this.pageInfo = document.getElementById(options.pageInfoId);
        this.rangeInfo = document.getElementById(options.rangeInfoId);
        this.rowsPerPageSelect = document.getElementById(options.rowsPerPageSelectId);
        this.downloadBtn = document.getElementById(options.downloadBtnId);

        this.columns = options.columns;

        this.init();
    }

    init() {
        // this.renderTable();
        this.attachEvents();
        this.fetchData();
    }

    attachEvents() {
        this.prevBtn.addEventListener('click', () => {
            this.gotoPage(this.currentPage - 1);
        });
        this.nextBtn.addEventListener('click', () => {
            this.gotoPage(this.currentPage + 1);
        })
        this.rowsPerPageSelect.addEventListener('change', (e) => {
            this.rowsPerPage = parseInt(e.target.value, 10);
            this.gotoPage(1);
        });
        this.downloadBtn.addEventListener('click', () => this.downloadCSV());
    }
    
    async fetchData() {
        const payload = {
            page: this.currentPage,
            limit: this.rowsPerPage
        }

        const res = await fetch(this.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        const json = await res.json();

        this.datatable = json.datatable;
        this.total = json.total;

        this.renderTable();
    }

    gotoPage(page) {
        this.currentPage = page;
        this.fetchData();
    }

    renderTable() {
        const start = (this.currentPage - 1) * this.rowsPerPage;
        const end = Math.min(start + this.rowsPerPage, this.total);
        const totalPages = Math.max(1, Math.ceil(this.total / this.rowsPerPage));

        this.tableBody.innerHTML = this.datatable.map(row => `
            <tr class="odd:bg-white even:bg-gray-50">
                ${this.columns.map(col => `<td class="border border-gray-300 px-3 py-2">${row[col] ?? ''}</td>`).join('')}
            </tr>
        `).join('');

        this.prevBtn.disabled = this.currentPage <= 1;
        this.nextBtn.disabled = this.currentPage >= totalPages;
        this.pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        this.rangeInfo.textContent = this.total 
            ? `Showing ${start + 1} to ${end} of ${this.total} entries` 
            : `No entries to show`;
    }

    async downloadCSV() {
        try {
            // fetch data from backend
            const response = await fetch("/api/all-current-survey-data", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
            });
            if (!response.ok) throw new Error("Something wrong please check with admin.");

            const res = await response.json();
            const data = res.datatable;
            
            if (!data.length) return;

            const header = Object.keys(data[0]);
            const escape = v => /[\",\\n]/.test(v) ? `"${String(v).replace(/"/g, '""')}"` : v;
            const csv = [header.join(','), ...data.map(r => header.map(h => escape(r[h])).join(','))].join('\n');

            const blob = new Blob(["\ufeff", csv], { type: 'text/csv;charset=utf-8;' }); // BOM for Excel
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'survey_result.csv';
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error(err);
        }
    }
}



export class DataTable {
    constructor(options) {
        this.data = options.data || [];
        this.rowsPerPage = options.rowsPerPage || 10;
        this.currentPage = 1;
        this.total = this.data.length;

        this.tableBody = document.getElementById(options.tableBodyId);
        this.prevBtn = document.getElementById(options.prevBtnId);
        this.nextBtn = document.getElementById(options.nextBtnId);
        this.pageInfo = document.getElementById(options.pageInfoId);
        this.rangeInfo = document.getElementById(options.rangeInfoId);
        this.rowsPerPageSelect = document.getElementById(options.rowsPerPageSelectId);
        this.downloadBtn = document.getElementById(options.downloadBtnId);

        this.columns = options.columns;

        this.downloadFileName = options.downloadFileName;

        this.init();
    }

    init() {
        this.attachEvents();
        this.renderTable();
    }

    attachEvents() {
        this.prevBtn.addEventListener('click', () => {
            this.gotoPage(this.currentPage - 1);
        });
        this.nextBtn.addEventListener('click', () => {
            this.gotoPage(this.currentPage + 1);
        })
        this.rowsPerPageSelect.addEventListener('change', (e) => {
            this.rowsPerPage = parseInt(e.target.value, 10);
            this.gotoPage(1);
        });
        this.downloadBtn.addEventListener('click', () => this.downloadCSV());
    }

    gotoPage(page) {
        this.currentPage = page;
        this.renderTable();
    }

    renderTable() {
        const start = (this.currentPage - 1) * this.rowsPerPage;
        const end = Math.min(start + this.rowsPerPage, this.total);
        const totalPages = Math.max(1, Math.ceil(this.total / this.rowsPerPage));
        const slice = this.data.slice(start, end);

        this.tableBody.innerHTML = slice.map(row => `
            <tr class="odd:bg-white even:bg-gray-50">
                ${this.columns.map(col => `<td class="border border-gray-300 px-3 py-2">${row[col] ?? ''}</td>`).join('')}
            </tr>
        `).join('');

        this.prevBtn.disabled = this.currentPage <= 1;
        this.nextBtn.disabled = this.currentPage >= totalPages;
        this.pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        this.rangeInfo.textContent = this.total 
            ? `Showing ${start + 1} to ${end} of ${this.total} entries` 
            : `No entries to show`;
    }

    async downloadCSV() {
        try {
                    
            if (!this.data.length) return;

            const header = Object.keys(this.data[0]);
            const escape = v => /[\",\\n]/.test(v) ? `"${String(v).replace(/"/g, '""')}"` : v;
            const csv = [header.join(','), ...this.data.map(r => header.map(h => escape(r[h])).join(','))].join('\n');

            const blob = new Blob(["\ufeff", csv], { type: 'text/csv;charset=utf-8;' }); // BOM for Excel
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.downloadFileName;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error(err);
        }
    }
}
