// datatable.js

export class DataTable {
    constructor(options) {
        this.data = options.data || [];
        this.rowsPerPage = options.rowsPerPage || 10;
        this.currentPage = 1;
        this.tableBody = document.getElementById(options.tableBodyId);
        this.prevBtn = document.getElementById(options.prevBtnId);
        this.nextBtn = document.getElementById(options.nextBtnId);
        this.pageInfo = document.getElementById(options.pageInfoId);
        this.rangeInfo = document.getElementById(options.rangeInfoId);
        this.rowsPerPageSelect = document.getElementById(options.rowsPerPageSelectId);
        this.downloadBtn = document.getElementById(options.downloadBtnId);

        this.init();
    }

    init() {
        this.renderTable();
        this.attachEvents();
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
    
    paginate() {
        const total = this.data.length;
        const totalPages = Math.max(1, Math.ceil(total / this.rowsPerPage));
        const clampedPage = Math.min(Math.max(this.currentPage, 1), totalPages);
        const start = (clampedPage - 1) * this.rowsPerPage;
        const end = Math.min(start + this.rowsPerPage, total);
        return {
            slice: this.data.slice(start, end),
            start,
            end,
            total,
            totalPages,
            page: clampedPage
        }
    }

    gotoPage(page) {
        this.currentPage = page;
        this.renderTable();
    }

    renderTable() {
        const { slice, start, end, total, totalPages, page } = this.paginate();
        this.tableBody.innerHTML = slice.map(row => `
            <tr class="odd:bg-white even:bg-gray-50">
                ${Object.values(row).map(val => `<td class="border border-gray-300 px-3 py-2">${val}</td>`).join('')}
            </tr>
        `).join('');

        this.prevBtn.disabled = page <= 1;
        this.nextBtn.disabled = page >= totalPages;
        this.pageInfo.textContent = `Page ${page} of ${totalPages}`;
        this.rangeInfo.textContent = total ? `Showing ${start + 1} to ${end} entries` : `No entries to show`;
    }

    downloadCSV() {
        if (!this.data.length) return;

        const header = Object.keys(this.data[0]);
        const escape = v => /[\",\\n]/.test(v) ? `"${String(v).replace(/"/g, '""')}"` : v;
        const csv = [header.join(','), ...this.data.map(r => header.map(h => escape(r[h])).join(','))].join('\n');
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'data.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    }
}
