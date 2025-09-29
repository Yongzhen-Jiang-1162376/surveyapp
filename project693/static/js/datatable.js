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
            <tr class="odd:bg-white even:bg-gray-50">
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




        // Open modal by simulating a click on a trigger
        console.log('logged')

        

        // HSOverlay.open('#closeSurveyModal');

        // const trigger = document.createElement("button");
        // trigger.setAttribute("data-hs-overlay", "#closeSurveyModal");

        // console.log('logged2')
        // document.body.appendChild(trigger);
        // trigger.click();
        // trigger.remove();

        // const confirmBtn = document.getElementById("confirmCloseSurvey");

        // if (!confirm("Are you sure to close this survey?")) return;

        // const handler = async function () {
        //     try {
        //         const res = await fetch('/api/close-survey', {
        //             method: 'POST',
        //             headers: { "Content-Type": "application/json" }
        //         });

        //         const data = await res.json();

        //         if (!res.ok || !data.success) {
        //             alert(data.message);
        //         } else {
        //             alert(data.message);
        //             window.location.reload();
        //         }
                
        //     } catch (err) {
        //         console.error(err);
        //         alert('Something went wrong');
        //     } finally {
        //         // close modal
        //         window.HSOverlay.close(modal)
        //         confirmBtn.removeEventListener("click", handler);
        //     }
        // }

        // confirmBtn.addEventListener("click", handler);
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
