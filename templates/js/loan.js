//{% load i18n %}
//{% load inventree_extras %}
//{% load generic %}

/**
 * Gets the fields for the loan user creation form
 * @returns fields for the loan user creation form
 * @see  constructForm
 */
function loanUserFields() {
    return {
        first_name: {},
        last_name: {},
        email: {},
        idn: {}
    };
}

/**
 * Gets the fields for the loan session creation form
 * @returns fields for the loan session creation form
 * @see constructForm
 */
function loanSessionFields() {
    return {
        stock: {
            help_text: '{% trans "Select stock item to loan" %}',
        },
        loan_user: {
            model: 'user', // Override our plugin's default model (which is 'loanuser') with (built-in)'user' for the dropdown to work
            icon: 'fa-user',
            secondary: {
                title: 'Add User',
                fields: loanUserFields()
            },
            help_text: '{% trans "User to loan the stock item to" %}',
        },
        quantity: {
            icon: 'fa-sitemap',
            help_text: '{% trans "Enter amount of this stock item to loan" %}',
        },
        loan_date: {
            icon: 'fa-calendar',
            help_text: '{% trans "Enter the date the item has been loaned on" %}',
        },
        due_date: {
            icon: 'fa-calendar-check',
            help_text: '{% trans "Enter the date the item is due to be returned" %}',
        },
        location: {
            icon: 'fa-clipboard',
            help_text: '{% trans "Optionally, enter the name of the location the item will be loaned to" %}',
        }
    };
}

// noinspection JSUnusedGlobalSymbols
/**
 * Launches a modal form to create a LoanSession
 * @see LoanSessionList
 */
function createNewLoanSession(options = {}) {
    const url = '/plugin/loan/api/loansession/'; // API endpoint for creating a new LoanSession - Shouldn't be hardcoded

    options.title = '{% trans "Loan Stock Item" %}';

    options.method = 'POST';

    options.create = true;

    // Fields for the form
    options.fields = loanSessionFields(options);

    constructForm(url, options);
}

// noinspection JSUnusedGlobalSymbols
/**
 * Launches a modal form to mark a LoanSession as returned
 * @todo Properly implement this. Only do barcode as otherwise you can just look it up in the table.
 * @param item_list
 * @param options
 */
function returnLoanSession(item_list, options = {}) {
    const modal = options.modal || createNewModal();
    options.modal = modal;

    let stock_item = null;

    // Extra form fields
    //var extra = makeNotesField();

    // Header content
    const header = `
    <div id='header-div'>
    </div>
    `;

    function updateStockItemInfo(stockitem) {
        const div = $(modal + ' #header-div');

        if (stockitem && stockitem.pk) {
            div.html(`
            <div class='alert alert-block alert-info'>
            <b>{% trans "Stock Item" %}</b></br>
            ${stockitem.part_detail.name}<br>
            <i>${stockitem.serial ? ('#' + stockitem.serial) : stockitem.quantity}</i>
            </div>
            `);
        } else {
            div.html('');
        }
    }

    barcodeDialog(
        '{% trans "Check Into Location" %}',
        {
            headerContent: header,
            //extraFields: extra,
            modal: modal,
            preShow: function() {
                modalSetSubmitText(modal, '{% trans "Check In" %}');
                modalEnable(modal, false);
            },
            onShow: function() {
            },
            onSubmit: function() {
                // Called when the 'check-in' button is pressed
                if (!stock_item) {
                    return;
                }

                const items = [];

                item_list.forEach(function(item) {
                    items.push({
                        pk: item.pk || item.id,
                        quantity: item.quantity,
                    });
                });

                const data = {
                    location: stock_item.pk,
                    notes: $(modal + ' #notes').val(),
                    items: items,
                };

                // Send API request
                inventreePut(
                    '{% url "api-stock-transfer" %}',
                    data,
                    {
                        method: 'POST',
                        success: function(response) {
                            // First hide the modal
                            $(modal).modal('hide');

                            if (options.success) {
                                options.success(response);
                            } else {
                                location.reload();
                            }
                        }
                    }
                );
            },
            onScan: function(response) {
                updateStockItemInfo(null);
                if ('stockitem' in response) {

                    const pk = response.stockitem.pk;

                    inventreeGet(`{% url "api-stock-list" %}${pk}/`, {}, {
                        success: function(response) {

                            stock_item = response;

                            updateStockItemInfo(stock_item);
                            modalEnable(modal, true);
                        },
                        error: function() {
                            // Barcode does *NOT* correspond to a StockLocation
                            showBarcodeMessage(
                                modal,
                                '{% trans "Barcode does not match a valid item" %}',
                                'warning',
                            );
                        }
                    });
                } else {
                    // Barcode does *NOT* correspond to a StockLocation
                    showBarcodeMessage(
                        modal,
                        '{% trans "Barcode does not match a valid item" %}',
                        'warning',
                    );
                }
            }
        }
    );
}

/**
 * Removes all filters from the table and sets the given filter to filterValue, removes it if it already is set.
 * @param table
 * @param filterKey
 * @param filterTarget
 * @param filterOptions
 * @param filterString filter to update
 * @param filterValue value to set the filter to
 */
function tableSetSingleFilter(table, filterKey, filterTarget, filterOptions, filterString, filterValue = true) {
    // Remove existing filters
    clearTableFilters(filterKey);

    // Gets the value of the string filter
    const table_param = table.bootstrapTable('getOptions').query_params[filterString];

    // Add or remove the filter
    if (table_param == null) {
        filters = addTableFilter(filterKey, filterString, filterValue);
    } else {
        filters = removeTableFilter(filterKey, filterString);
    }

    // Update the filter list (including reshowing the filter list
    reloadTableFilters(table, filters, filterOptions);
    setupFilterList(filterKey, table, filterTarget, filterOptions);
}

/**
 * Renders a badge for the active/restricted state of a loan user
 * @param value active/restricted state of a loan user
 * @returns pill indicating the active/restricted state of a loan user
 */
function activeRestrictedBadge(value) {
    if (!value) {
        return `<span class='badge badge-right rounded-pill bg-success'>{% trans "Allowed" %}</span>`;
    } else {
        return `<span class='badge badge-right rounded-pill bg-danger'>{% trans "Restricted" %}</span>`;
    }
}

/**
 * Renders a badge for the active/disabled state of a loan user
 * @param value active/disabled state of a loan user
 * @returns pill indicating the active/disabled state of a loan user
 */
function activeDisabledBadge(value) {
    if (value) {
        return `<span class='badge badge-right rounded-pill bg-success'>{% trans "Active" %}</span>`;
    } else {
        return `<span class='badge badge-right rounded-pill bg-danger'>{% trans "Disabled" %}</span>`;
    }
}

// noinspection JSUnusedGlobalSymbols
/**
 * Loads a loan session table
 * @param table HTML table to load the loan session table into
 * @param options Options for the table
 * Options:
 * - url: URL to load the table from
 * - params: Query parameters when requesting loan sessions
 * - disableFilters: Disable the filters for the table
 */
function loadLoanTable(table, options= {}) {
    options.params = options.params || {};

    let filters = {};

    if (!options.disableFilters) {
        const filterTarget = options["filterTarget"] || '#filter-list-loan';
        const filterKey = options["filterKey"] || options.name || 'loan';

        // Add the overdue/current/returned filters. Also, reload the table when these filters are executed. This is a work-around for not being able to implement default filters for custom plugin tables
        let filterOptions = {
            download: false, // TODO add download functionality in the api
            singular_name: '{% trans "loan session" %}',
            plural_name: '{% trans "loan sessions" %}',
            custom_actions: [
                {
                    actions: [
                        {
                            icon: 'fa-calendar-times',
                            title: '{% trans "Overdue" %}',
                            label: 'overdue',
                            callback: () => tableSetSingleFilter(table, filterKey, filterTarget, filterOptions, 'overdue')
                        },
                        {
                            icon: 'fa-calendar',
                            title: '{% trans "Loaned" %}',
                            label: 'current',
                            callback: () => tableSetSingleFilter(table, filterKey, filterTarget, filterOptions, 'current')
                        },
                        {
                            icon: 'fa-calendar-check',
                            title: '{% trans "Returned" %}',
                            label: 'returned',
                            callback: () => tableSetSingleFilter(table, filterKey, filterTarget, filterOptions, 'returned')
                        }
                    ],
                    icon: 'fa-filter',
                    title: '{% trans "Loan Filters" %}',
                    label: 'loan',
                }
            ]
        }

        // Get the previous filters set by the user.
        filters = loadTableFilters(filterKey, options.params);

        // Setup buttons above the table/filters for the table
        setupFilterList(filterKey, table, filterTarget, filterOptions);
    }

    filters = Object.assign(filters, options.params);

    // Create the columns for the table
    let col;
    const columns = [];

    // Part the stock is associated with
    col = {
        field: 'part_item',
        title: 'Part',
        visible: true,
        formatter: function(value, row) {
            return partDetail(row.stock_detail.part_detail, {
                thumb: true,
                link: true,
                icons: true,
            });
        }
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Stock item serial number
    col = {
        field: 'quantity',
        sortName: 'stock',
        title: 'Stock Item',
        formatter: function(value, row) {
            let val;

            // Does the stock have a serial number?
            if (row.stock_detail.serial && row.stock_detail.quantity === 1) {
                // If there is a single unit with a serial number, use the serial number
                val = '# ' + row.stock_detail.serial;
            } else {
                // Format floating point numbers with this one weird trick
                val = formatDecimal(row.quantity);

                if (row.stock_detail.part_detail && row.stock_detail.part_detail.units) {
                    val += ` ${row.stock_detail.part_detail.units}`;
                }
            }

            return renderLink(val, `/stock/item/${row.stock_detail.pk}/`);
        }
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    col = {
        field: 'loan_user',
        title: 'User',
        visible: true
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Date loaned
    col = {
        field: 'loan_date',
        title: 'Loan Date',
        visible: true,
        sortable: true,
        formatter: function(value) {
            return renderDate(value);
        }
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Date due
    col = {
        field: 'due_date',
        title: 'Due Date',
        visible: true,
        sortable: true,
        formatter: function(value) {
            return renderDate(value);
        }
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Location lent
    col = {
        field: 'location',
        title: 'Location Lent',
        visible: true,
        formatter: function(value) {
            if (value == null) {
                return '{% trans Unknown %}';
            }
            return shortenString(value);
        }
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Returned
    col = {
        field: 'returned_date',
        title: 'Returned Date',
        visible: true,
        formatter: function(value) {
            return renderDate(value);
        }
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Show the table
    table.inventreeTable({
        url: options.url || '/plugin/loan/api/loansession/', // Hardcoded API endpoint (shouldn't be)
        method: 'get',
        name: 'loan',
        original: options.params,
        sidePagination: 'server',
        queryParams: filters,
        columns: columns,
        uniqueId: 'pk',
        idField: 'pk',
        formatNoMatches: function() {
            return '{% trans "No loan sessions found" %}';
        }
    });
}

// noinspection JSUnusedGlobalSymbols
/**
 * Loads a loan user table
 * @param table HTML table to load the loan user table into
 * @param options Options for the table
 * Options:
 * - url: URL to load the table from
 * - params: Query parameters when requesting loan users
 * - disableFilters: Disable the filters for the table
 */
function loadUserTable(table, options = {}) {
    options.params = options.params || {};

    let filters = {};

    if (!options.disableFilters) {
        const filterTarget = options["filterTarget"] || '#filter-list-user';
        const filterKey = options["filterKey"] || options.name || 'user';

        // Add the active/restricted filters. Also, reload the table when these filters are executed. This is a work-around for not being able to implement default filters for custom plugin tables
        let filterOptions = {
            download: false, // TODO add download functionality in the api
            singular_name: '{% trans "loan user" %}',
            plural_name: '{% trans "loan users" %}',
            custom_actions: [
                {
                    actions: [
                        {
                            icon: 'fa-user',
                            title: '{% trans "Active" %}',
                            label: 'active',
                            callback: () => tableSetSingleFilter(table, filterKey, filterTarget, filterOptions, 'active')
                        }
                    ],
                    icon: 'fa-filter',
                    title: '{% trans "User Filters" %}',
                    label: 'user',
                }
            ]
        }

        // Get the previous filters set by the user.
        filters = loadTableFilters(filterKey, options.params);

        // Setup buttons above the table/filters for the table
        setupFilterList(filterKey, table, filterTarget, filterOptions);
    }

    filters = Object.assign(filters, options.params);

    // Create the columns for the table
    let col;
    const columns = [];

    // First name
    col = {
        field: 'first_name',
        title: 'First Name',
        visible: true
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Last name
    col = {
        field: 'last_name',
        title: 'Last Name',
        visible: true
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Email
    col = {
        field: 'email',
        title: 'Email',
        visible: true,
        searchable: true,
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Restricted State
    col = {
        field: 'restricted',
        title: 'Restricted',
        visible: true,
        sortable: true,
        formatter: activeRestrictedBadge
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Active State
    col = {
        field: 'active',
        title: 'Active',
        visible: true,
        formatter: activeDisabledBadge
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Show the table
    table.inventreeTable({
        url: options.url || '/plugin/loan/api/loanuser/',
        method: 'get',
        name: 'loanuser',
        original: options.params,
        sidePagination: 'server', // Allows the server to check for RIN number (since it should be hidden from the user)
        queryParams: filters,
        columns: columns,
        uniqueId: 'pk',
        idField: 'pk',
        formatNoMatches: function() {
            return '{% trans "No loan users found" %}';
        }
    });

}