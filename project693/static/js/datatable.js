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

        this.notyf = new Notyf({
            duration: 3000,
            position: { x: 'right', y: 'top' },
            dismissible: true,
            types: [
                {
                    type: 'warning',
                    background: '#f59e0b', // Tailwind amber-500
                    icon: {
                        className: 'material-icons',
                        tagName: 'i',
                        text: 'warning'
                    }
                }
            ]
        })

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
            this.downloadBtn.addEventListener('click', (e) => {
                const type = e.target.dataset.downloadType;

                if (type === 'meta-data') {
                    this.downloadMetaCSV();
                } else {
                    this.downloadCSV();
                }
            });
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
        if (this.pageInfo) {
            this.pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        }
        this.rangeInfo.textContent = this.total 
            ? `Showing ${start + 1} to ${end} of ${this.total} entries` 
            : `No entries to show`;
        
        // close cycle action
        this.tableBody.querySelectorAll('.close-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                const row = this.datatable[index];
                console.log(row);
                this.closeSurvey(btn);
            });
        });

        // delete cycle action
        this.tableBody.querySelectorAll('.delete-cycle-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                const row = this.datatable[index];
                const cycle_id = row.cycle_id;
                console.log(row.cycle_id);

                if (!confirm("Are you sure you want to delete this survey cycle?")) return;

                this.deleteSurveyCycle(cycle_id, btn);
            });
        });
        
        // recalculate & refresh historical cycle
        this.tableBody.querySelectorAll('.recalculate-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                const row = this.datatable[index];
                const cycle_id = row.cycle_id;
                console.log(row.cycle_id);

                // if (!confirm("Are you sure you want to delete this survey cycle?")) return;
                this.refreshSurveyCycle(cycle_id, btn);
            });
        });

        // recalculate & refresh all survey data
        this.tableBody.querySelectorAll('.recalculate-all-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                console.log('updating all survey data')
                // const row = this.datatable[index];
                // const cycle_id = row.cycle_id;
                // console.log(row.cycle_id);

                // if (!confirm("Are you sure you want to delete this survey cycle?")) return;
                this.refreshAllSurveyData(btn);
            });
        });

        this.tableBody.querySelectorAll('.download-cycle-raw-data-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                const row = this.datatable[index];
                console.log(row.cycle_id);
                this.downloadCycleResultsCSV(row.cycle_id);
            });
        });

        this.tableBody.querySelectorAll('.download-all-raw-data-btn').forEach((btn, index) => {
            btn.addEventListener('click', () => {
                console.log('downloading all data...');
                // const row = this.datatable[index];
                // console.log(row.cycle_id);
                this.downloadAllResultsCSV();
            });
        });

        let detailGrid = null;

        this.tableBody.querySelectorAll('tr').forEach((row, index) => {
            row.addEventListener('click', async (e) => {

                if (e.target.closest('button')) return;

                const row = e.target.closest('tr');
                if (!row) return;

                const rowsArray = Array.from(this.tableBody.querySelectorAll('tr'));
                const rowIndex = Array.from(this.tableBody.children).indexOf(row);
                const cycle = this.datatable[rowIndex];
                console.log('Clicked cycle: ', cycle.cycle_id);

                if (!cycle) return;

                // Highlight selected row
                const isAlreadySelected = row.classList.contains('!bg-blue-200');

                // Remove highligh from all rows
                rowsArray.forEach(r => r.classList.remove('!bg-blue-200'));

                if (!isAlreadySelected) {
                    row.classList.add('!bg-blue-200');
                }
                
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

                // console.log(data)

                // Set the table headers
                if (data.length) {

                    if (!detailGrid) {
                        detailGrid = new gridjs.Grid({
                            resizable: true,
                            columns: [
                                { name: 'Internal Id', hidden: true },
                                { name: 'Session Id' },
                                { name: 'Ques. Seq', width: '150px' },
                                { name: 'Submitted At', width: '180px' },
                                { name: 'Response Time', width: '180px' },
                                { name: 'Invasive Plant Name', width: '280px' },
                                { name: 'Non-Invasive Plant Name', width: '280px' },
                                { name: 'Selected Plant Name', width: '280px' },
                                {
                                    id: 'action',
                                    name: '',
                                    sort: false,
                                    search: false,
                                    // width: '80px',
                                    formatter: (_, row) => {
                                        return gridjs.h('div', { 
                                        className: 'flex justify-center items-center' // center horizontally + vertically
                                        }, [
                                        gridjs.h('button', {
                                            className: 'text-red-600 hover:text-red-800 cursor-pointer flex items-center justify-center',
                                            onClick: async (e) => {
                                                e.stopPropagation();
                                                const internalId = row.cells[0].data;
                                                console.log('Delete clicked for ID:', internalId);

                                                if (!confirm("Are you sure you want to delete this survey record?")) return;

                                                try {
                                                    const res = await fetch('/api/delete-survey-choice-by-id', {
                                                        method: 'POST',
                                                        headers: { 'Content-Type': 'application/json' },
                                                        body: JSON.stringify({ id: internalId })
                                                    });

                                                    const data = await res.json();

                                                    if(!res.ok || !data.success) {
                                                        this.notyf.open({
                                                            type: 'warning',
                                                            message: data.message,
                                                            duration: 5000
                                                        });
                                                    } else {
                                                        this.notyf.success("Survey record deleted successfully");
                                                        const newData = detailGrid.config.data
                                                            .filter(r => r[0] !== internalId);
                                                        
                                                        if (newData.length === 0) {
                                                            window.location.reload();
                                                        } else {
                                                            detailGrid.updateConfig({ data: newData }).forceRender();
                                                        }
                                                    }
                                                } catch (err) {
                                                    console.log(err)
                                                    alert("Something went wrong", "error");
                                                }
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
                                th: "border px-1 py-2 text-left text-sm font-semibold uppercase !text-gray-800 whitespace-normal break-words",
                                td: "border px-1 py-2 whitespace-normal break-words"
                            },
                            // afterRender: () => {
                            //     lucide.createIcons();
                            // }
                        });
                        detailGrid.render(detailDiv);
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

    async downloadMetaCSV() {
        try {
            // fetch data from backend
            const response = await fetch("/api/all-survey-meta-data", {
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
            a.download = 'survey_meta_result.csv';
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

    async downloadAllResultsCSV() {
        try {
            const response = await fetch("/api/download-all-survey-data", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // body: JSON.stringify({ cycle_id })
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

    async closeSurvey(button) {

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
            // hide modal immediately

            modal.classList.add("hidden");

            if (button) {
                button.disabled = true;
                button.innerHTML = `
                    <svg class="animate-spin h-4 w-4 mr-2 inline text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor"
                            d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z">
                        </path>
                    </svg> Closing...
                `;
            }

            try {
                const res = await fetch(`/api/close-survey`, {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({})
                });

                const data = await res.json();

                if (!res.ok || !data.success) {
                    this.notyf.open({
                        type: 'warning',
                        message: data.message,
                        duration: 5000
                    });
                    // this.showToast(data.message, "error");
                    if (button) {
                        button.disabled = false;
                        button.textContent = "Close";

                        return false;
                    }
                }
                window.location.reload()
            } catch (err) {
                console.error(err);
                this.notyf.error("Something is wrong. Please contact your administrator.");
            } finally {
                modal.classList.add("hidden");
                cancelBtn.removeEventListener("click", cancelHandler);
                confirmBtn.removeEventListener("click", confirmHandler);
            }
        };

        confirmBtn.addEventListener("click", confirmHandler);
    }

    async deleteSurveyCycle(cycle_id, button) {
        if (button) {
            button.disabled = true;
            button.innerHTML = `
                <svg class="animate-spin h-4 w-4 mr-2 inline text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z">
                    </path>
                </svg> Deleting...
            `;
        }

        try {
            const res = await fetch(`/api/delete-survey-cycle-by-id`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cycle_id })
            });

            const data = await res.json();

            if (!res.ok || !data.success) {
                this.notyf.error('Failed to delete survey cycle.')
                if (button) {
                    button.disabled = false;
                    button.textContent = "Refresh";
                }
                return false;
            }
            window.location.reload()
        } catch (err) {
            console.error(err)
            // alert('Error deleting survey cycle');
            this.notyf.error('Failed to delete survey cycle.')
            if (button) {
                button.disabled = false;
                button.textContent = "Refresh";
            }
            return false;
        }
    }

    async refreshSurveyCycle(cycle_id, button) {
        if (button) {
            button.disabled = true;
            button.innerHTML = `
                <svg class="animate-spin h-4 w-4 mr-2 inline text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z">
                    </path>
                </svg> Updating...
            `;
        }

        try {
            const res = await fetch(`/api/refresh-survey-cycle-by-id`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cycle_id })
            });

            const data = await res.json();

            if (!res.ok || !data.success) {
                this.notyf.warning('Failed to update survey cycle.');
                if (button) {
                    button.disabled = false;
                    button.textContent = "Update";
                }
                return false;
            }
            window.location.reload()
        } catch (err) {
            console.error(err)
            this.notyf.warning('Error updating survey cycle');
            if (button) {
                button.disabled = false;
                button.textContent = "Update";
            }
            return false;
        }
    }


    async refreshAllSurveyData(button) {
        if (button) {
            button.disabled = true;
            button.innerHTML = `
                <svg class="animate-spin h-4 w-4 mr-2 inline text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z">
                    </path>
                </svg> Updating...
            `;
        }

        try {
            const res = await fetch(`/api/refresh-all-survey-data`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // body: JSON.stringify({ cycle_id })
            });

            const data = await res.json();

            if (!res.ok || !data.success) {
                this.notyf.warning('Failed to update survey data.');
                if (button) {
                    button.disabled = false;
                    button.textContent = "Update";
                }
                return false;
            }
            window.location.reload()
        } catch (err) {
            console.error(err)
            this.notyf.warning('Error updating survey data.');
            if (button) {
                button.disabled = false;
                button.textContent = "Update";
            }
            return false;
        }
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

            const visibleColumns = this.columns;

            const escape = v => /[\",\\n]/.test(v) ? `"${String(v).replace(/"/g, '""')}"` : v;
            // const csv = [header.join(','), ...this.data.map(r => data_header.map(h => escape(r[h])).join(','))].join('\n');
            const csv = [visibleColumns.join(','), ...this.data.map(r => visibleColumns.map(h => escape(r[h])).join(','))].join('\n');

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
