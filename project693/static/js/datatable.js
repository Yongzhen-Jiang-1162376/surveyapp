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

    showToast(message, type = "success") {
        const container = document.getElementById("toastContainer");
        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `
            flex items-center justify-between px-4 py-2 rounded shadow text-white
            ${type === "success" ? "bg-green-600" : "bg-red-600"}
            animate-fadeIn
        `;
        toast.textContent = message;

        container.appendChild(toast);

        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.classList.add("animate-fadeOut");
            toast.addEventListener("animationend", () => toast.remove());
        }, 3000);
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
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => this.downloadCSV());
        }
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
            <tr class="odd:bg-white even:bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors duration-200">
                ${this.columns.map(col => {
                    if (col.key) {
                        return `<td class="border border-gray-300 px-3 py-2">${row[col.key] ?? ''}</td>`
                    } else if (col.render) {
                        return `<td class="border border-gray-300 px-3 py-2">${col.render(row)}</td>`
                    } else {
                        return `<td class="border border-gray-300 px-3 py-2">${row[col] ?? ''}</td>`
                    }
                }).join('')}
            </tr>
        `).join('');

        this.prevBtn.disabled = this.currentPage <= 1;
        this.nextBtn.disabled = this.currentPage >= totalPages;
        this.pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        this.rangeInfo.textContent = this.total 
            ? `Showing ${start + 1} to ${end} of ${this.total} entries` 
            : `No entries to show`;
        
        this.tableBody.querySelectorAll('.close-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                const row = this.datatable[index];
                console.log(row.cycle_id);
                this.closeSurvey();
            });
        });

        this.tableBody.querySelectorAll('.download-cycle-raw-data-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                const row = this.datatable[index];
                console.log(row.cycle_id);
                this.downloadCycleResultsCSV(row.cycle_id);
            });
        });

        let detailGrid = null;

        this.tableBody.querySelectorAll('tr').forEach((row, index) => {
            row.addEventListener('click', async () => {
                const cycle = this.datatable[index];
                console.log('Clicked cycle: ', cycle.cycle_id);

                // Highlight selected row
                this.tableBody.querySelectorAll('tr').forEach(r => r.classList.remove('bg-gray-200'));
                row.classList.add('bg-gray-200');

                // show detail table
                const detailContainer = document.getElementById('detailTableContainer');
                detailContainer.classList.remove('hidden');

                // Fetch detail data for this cycle
                const res = await fetch(`/api/survey-cycle-detail`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cycle_id: cycle.cycle_id })
                });
                const result = await res.json();
                const data = result.datatable || [];

                const detailDiv = document.getElementById("detailTable");

                // clear any existing Grid.js instance
                // if (this.detailGrid) {
                //     this.detailGrid.destroy();
                //     this.detailGrid = null;
                // }

                console.log(data)

                // Set the table headers
                if (data.length) {

                    if (!detailGrid) {
                        detailGrid = new gridjs.Grid({
                            columns: [
                                { name: 'Internal Id', hidden: true },
                                'Session Id',
                                { name: 'Ques. Seq', width: '150px' },
                                { name: 'Submitted At', width: '180px' },
                                { name: 'Response Time', width: '180px' },
                                { name: 'Invasive Plant Name', width: '280px' },
                                { name: 'Non-Invasive Plant Name', width: '280px' },
                                'Selected Plant Name',
                                {
                                    name: '',
                                    sort: false,
                                    search: false,
                                    width: '80px',
                                    formatter: (_, row) => {
                                        return gridjs.h('div', { 
                                        className: 'flex justify-center items-center' // center horizontally + vertically
                                        }, [
                                        gridjs.h('button', {
                                            className: 'text-red-600 hover:text-red-800 cursor-pointer flex items-center justify-center',
                                            onClick: (e) => {
                                            e.stopPropagation();
                                            const internalId = row.cells[0].data;
                                            console.log('Delete clicked for ID:', internalId);
                                            }
                                        }, gridjs.html(`
                                            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none"
                                                stroke="currentColor" stroke-width="2">
                                            <path d="M3 6h18"></path>
                                            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                                            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                                            <line x1="10" y1="11" x2="10" y2="17"></line>
                                            <line x1="14" y1="11" x2="14" y2="17"></line>
                                            </svg>
                                        `))
                                        ]);
                                    }
                                }
                            ],
                            data: data.map(row => [
                                row[0],
                                row[1],
                                row[2],
                                row[3],
                                row[4],
                                row[6],
                                row[8],
                                row[10],
                                null
                            ]),
                            pagination: { enabled: true, limit: 10 },
                            search: true,
                            sort: false,
                            className: {
                                table: "w-full border-collapse border border-gray-300",
                                th: "border px-3 py-2 text-left text-sm font-semibold uppercase !text-gray-800",
                                td: "border px-3 py-2 whitespace-normal break-words"
                            },
                            afterRender: () => {
                                lucide.createIcons();
                            }
                        }).render(detailDiv);
                        lucide.createIcons();
                    } else {
                        detailGrid.updateConfig({
                            data: data.map(row => [
                                row[0],
                                row[1],
                                row[2],
                                row[3],
                                row[4],
                                row[6],
                                row[8],
                                row[10],
                                null
                            ])
                        }).forceRender();

                        lucide.createIcons();
                    }
                } else {
                    detailDiv.innerHTML = `<div class="text-gray-500">No detail data found.</div>`;
                }
            });
        });

        lucide.createIcons();
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

    async fetchCycleDataCSV(cycle_id, fileName, api_path) {
        try {
            const response = await fetch(`/api/${api_path}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify( { cycle_id })
            });
            if (!response.ok) throw new Error('Failed to fetch cycle data');

            const res = await response.json();
            const data = res.datatable;
            if (!data.length) return null;

            const header = Object.keys(data[0]);
            const escape = v => /[\",\\n]/.test(v) ? `"${String(v).replace(/"/g, '""')}"` : v;
            const csv = [header.join(','), ...data.map(r => header.map(h => escape(r[h])).join(','))].join('\n');

            return { fileName, content: "\ufeff" + csv };
        } catch (err) {
            console.error(err);
            return null;
        }
    }

    async downloadCycleResultsCSV(cycle_id) {
        try {
            const response = await fetch("/api/download-survey-cycle-data-by-cycle-id", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cycle_id })
            });

            if (!response.ok) throw new Error('Failed to fetch zip file');

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = 'survey_results.zip';
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error(err);
        }
    }

    /*
    async downloadCycleResultsCSV(cycle_id) {
        const files = {};

        let result = await this.fetchCycleDataCSV(
            cycle_id, 
            'survey_raw_data.csv', 
            'all-survey-data-by-cycle-id'
        );
        if (result) {
            files[result.fileName] = strToU8(result.content);
        }

        result = await this.fetchCycleDataCSV(
            cycle_id, 
            'beta_score_by_invasive_type_histogram.csv', 
            'beta-score-by-invasive-type-histogram-by-cycle-id'
        );
        if (result) {
            files[result.fileName] = strToU8(result.content);
        }

        result = await this.fetchCycleDataCSV(
            cycle_id, 
            'win_loss_by_plant.csv', 
            'win-loss-by-plant-by-cycle-id'
        );
        if (result) {
            files[result.fileName] = strToU8(result.content);
        }

        result = await this.fetchCycleDataCSV(
            cycle_id, 
            'beta_score_heat_map_by_plant.csv', 
            'beta-score-heat-map-by-plant-by-cycle-id'
        );
        if (result) {
            files[result.fileName] = strToU8(result.content);
        }

        result = await this.fetchCycleDataCSV(
            cycle_id, 
            'beta_score_with_win_percentage_by_plant.csv', 
            'beta-score-win-percentage-by-cycle-id'
        );
        if (result) {
            files[result.fileName] = strToU8(result.content);
        }

        if (Object.keys(files).length === 0) return;

        const zipped = zipSync(files);
        const blob = new Blob([zipped], { type: 'application/zip' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'survey_results.zip';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);

        // try {
        //     // fetch data from backend
        //     const response = await fetch("/api/all-survey-data-by-cycle-id", {
        //         method: 'POST',
        //         headers: {
        //             'Content-Type': 'application/json'
        //         },
        //         body: JSON.stringify({
        //             cycle_id
        //         })
        //     });
        //     if (!response.ok) throw new Error("Something wrong please check with admin.");

        //     const res = await response.json();
        //     const data = res.datatable;
            
        //     if (!data.length) return;

        //     const header = Object.keys(data[0]);
        //     const escape = v => /[\",\\n]/.test(v) ? `"${String(v).replace(/"/g, '""')}"` : v;
        //     const csv = [header.join(','), ...data.map(r => header.map(h => escape(r[h])).join(','))].join('\n');

        //     const blob = new Blob(["\ufeff", csv], { type: 'text/csv;charset=utf-8;' }); // BOM for Excel
        //     const url = URL.createObjectURL(blob);
        //     const a = document.createElement('a');
        //     a.href = url;
        //     a.download = 'survey_result.csv';
        //     document.body.appendChild(a);
        //     a.click();
        //     a.remove();
        //     URL.revokeObjectURL(url);
        // } catch (err) {
        //     console.error(err);
        // }
    }
    */

    async closeSurvey() {

        const modal = document.getElementById("closeSurveyModal");
        const confirmBtn = document.getElementById("confirmCloseSurvey");
        const cancelBtn = document.getElementById("cancelCloseSurvey");

        // show modal
        modal.classList.remove("hidden");

        // cancel handler
        const cancelHandler = () => {
            modal.classList.add("hidden");
            cancelBtn.removeEventListener("click", cancelHandler);
            confirmBtn.removeEventListener("click", confirmHandler);
        };

        cancelBtn.addEventListener("click", cancelHandler);

        // confirm handler
        const confirmHandler = async () => {
            try {
                const res = await fetch('/api/close-survey', {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    // body: JSON.stringify({ cycle_id })
                });

                const data = await res.json();

                if (!res.ok || !data.success) {
                    // alert(data.message);
                    this.showToast(data.message, "error");
                } else {
                    // alert(data.message);
                    this.showToast(data.message, "success");
                    setTimeout(() => window.location.reload(), 1000);
                }
            } catch (err) {
                console.error(err);
                // alert("Something went wrong");
                this.showToast("Something went wrong", "error");
            } finally {
                modal.classList.add("hidden");
                cancelBtn.removeEventListener("click", cancelHandler);
                confirmBtn.removeEventListener("click", confirmHandler);
            }
        };

        confirmBtn.addEventListener("click", confirmHandler);

    }
}



export class DataTable {
    constructor(options) {
        this.data = options.data.rows || [];
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
        this.dataColumns = options.data.columns;

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
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => this.downloadCSV());
        }
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

            const header = this.columns;
            const data_header = this.dataColumns;

            const escape = v => /[\",\\n]/.test(v) ? `"${String(v).replace(/"/g, '""')}"` : v;
            const csv = [header.join(','), ...this.data.map(r => data_header.map(h => escape(r[h])).join(','))].join('\n');

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
