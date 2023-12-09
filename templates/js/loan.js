//{% load i18n %}
//{% load inventree_extras %}
//{% load generic %}

function loanUserFields(options={}) {
    var fields = {
        first_name: {},
        last_name: {},
        email: {},
        idn: {}
    }

    return fields;
}

function loanSessionFields(options={}) {
    var fields = {
        stock: {
            help_text: '{% trans "Select stock item to loan" %}',
        },
        /*
        loan_user: {
            label: "foo",
            before: "obamna",
            prefix: "prefix",
            after: "after",
            field_suffix: "suffix",
            secondary: 'loanuser'
        },
         */
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
        },
        location: {
            icon: 'fa-clipboard',
            help_text: '{% trans "Optionally, enter the name of the location the item will be loaned to" %}',
        }
    }

    return fields;
}

function createNewLoanSession(options = {}) {
    const url = '/plugin/loan/api/loansession/';

    options.title = '{% trans "Loan Stock Item" %}';

    options.method = 'POST';

    options.create = true;

    options.fields = loanSessionFields(options);

    constructForm(url, options);
}

function returnLoanSession(item_list, options = {}) {
    var modal = options.modal || createNewModal();
    options.modal = modal;

    var stock_item = null;

    // Extra form fields
    //var extra = makeNotesField();

    // Header content
    var header = `
    <div id='header-div'>
    </div>
    `;

    function updateStockItemInfo(stockitem) {
        var div = $(modal + ' #header-div');

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

                var items = [];

                item_list.forEach(function(item) {
                    items.push({
                        pk: item.pk || item.id,
                        quantity: item.quantity,
                    });
                });

                var data = {
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
                        success: function(response, status) {
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

                    var pk = response.stockitem.pk;

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

function getTrackingTableColumns() {
    var col = null;
    var columns = []

    // Part the stock is associated with
    col = {
        field: 'part_item',
        title: 'Part',
        visible: true,
        sortable: true,
        formatter: function(value, row) {
            return partDetail(row.stock_detail.part_detail, {
                thumb: true,
                link: true,
                icons: true,
            });
        }
    }

    columns.push(col);

    // Stock item serial number
    col = {
        field: 'quantity',
        sortName: 'stock',
        title: 'Stock Item',
        sortable: true,
        formatter: function(value, row) {
            var val = '';

            // Does the stock have a serial number?
            if (row.stock_detail.serial && row.stock_detail.quantity == 1) {
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

    columns.push(col);

    col = {
        field: 'loan_user',
        title: 'User',
        visible: true,
        sortable: true
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

    columns.push(col);

    // Location lent
    col = {
        field: 'location',
        title: 'Location Lent',
        visible: true,
        sortable: true,
        formatter: function(value) {
            if (value == null) {
                return '{% trans Unknown %}';
            }
            return shortenString(value);
        }
    }

    columns.push(col);

    // Returned
    col = {
        field: 'returned_date',
        title: 'Returned Date',
        visible: true,
        sortable: true,
        formatter: function(value) {
            return renderDate(value);
        }
    }

    columns.push(col);

    return columns;
}

function getLoanTableColumns() {
    var col = null;
    var columns = []

    // First name
    col = {
        field: 'first_name',
        title: 'First Name',
        visible: true,
        sortable: true
    }
    columns.push(col);

    // Last name
    col = {
        field: 'last_name',
        title: 'Last Name',
        visible: true,
        sortable: true
    }
    columns.push(col);

    // Email
    col = {
        field: 'email',
        title: 'Email',
        visible: true,
        sortable: true,
        searchable: true,
    }
    columns.push(col);

    // Restricted
    col = {
        field: 'restricted',
        title: 'Restricted',
        visible: true,
        sortable: true,
        formatter: function(value) {
            if (value) {
                return `<span class='badge badge-right rounded-pill bg-success'>{% trans "Allowed" %}</span>`;
            } else {
                return `<span class='badge badge-right rounded-pill bg-danger'>{% trans "Restricted" %}</span>`;
            }
        }
    }
    columns.push(col);

    // Active
    col = {
        field: 'active',
        title: 'Active',
        visible: true,
        sortable: true,
        formatter: function(value) {
            if (value) {
                return `<span class='badge badge-right rounded-pill bg-success'>{% trans "Active" %}</span>`;
            } else {
                return `<span class='badge badge-right rounded-pill bg-danger'>{% trans "Disabled" %}</span>`;
            }
        }
    }
    columns.push(col);

    return columns;
}

function loadLoanTable(table, options={}) {
    var columns = getTrackingTableColumns();

    const filterTarget = options.filterTarget || '#filter-list-loan';
    const filterKey = options.filterKey || options.name || 'loan';

    let filters = loadTableFilters(filterKey, options.params);

    // Add the overdue/current/returned filters. Also, reload the table when these filters are executed. This is a work-around for not being able to implement default filters for custom plugin tables
    let filterOptions = {
        singular_name: '{% trans "loan session" %}',
        plural_name: '{% trans "loan sessions" %}',
        custom_actions: [
            {
                actions: [
                    {
                        icon: 'fa-calendar-times',
                        title: '{% trans "Overdue" %}',
                        label: 'overdue',
                        callback: function(data) {
                            clearTableFilters(filterKey);
                            const overdue = !table.bootstrapTable('getOptions').query_params['overdue'];

                            if (overdue) {
                                filters = addTableFilter(filterKey, 'overdue', 'true');
                            } else {
                                filters = removeTableFilter(filterKey, 'overdue');
                            }

                            reloadTableFilters(table, filters, filterOptions);
                            setupFilterList(filterKey, table, filterTarget, filterOptions);
                        }
                    },
                    {
                        icon: 'fa-calendar',
                        title: '{% trans "Loaned" %}',
                        label: 'current',
                        callback: function(data) {
                            clearTableFilters(filterKey);
                            const current = !table.bootstrapTable('getOptions').query_params['current'];

                            if (current) {
                                filters = addTableFilter(filterKey, 'current', 'true');
                            } else {
                                filters = removeTableFilter(filterKey, 'current');
                            }

                            reloadTableFilters(table, filters, filterOptions);
                            setupFilterList(filterKey, table, filterTarget, filterOptions);
                        }
                    },
                    {
                        icon: 'fa-calendar-check',
                        title: '{% trans "Returned" %}',
                        label: 'returned',
                        callback: function(data) {
                            clearTableFilters(filterKey);
                            const returned = !table.bootstrapTable('getOptions').query_params['returned'];

                            if (returned) {
                                filters = addTableFilter(filterKey, 'returned', 'true');
                            } else {
                                filters = removeTableFilter(filterKey, 'returned');
                            }

                            reloadTableFilters(table, filters, filterOptions);
                            setupFilterList(filterKey, table, filterTarget, filterOptions);
                        }
                    }
                ],
                icon: 'fa-filter',
                title: '{% trans "Loan Filters" %}',
                label: 'loan',
            }
        ]
    }

    // Setup buttons above the table
    setupFilterList(filterKey, table, filterTarget, filterOptions);

    filters = Object.assign(filters, options.params);

    table.inventreeTable({
        url: '/plugin/loan/api/loansession/',
        method: 'get',
        name: 'loan',
        queryParams: filters,
        columns: columns,
        uniqueId: 'pk',
        idField: 'pk',
        formatNoMatches: function() {
            return '{% trans "No loan sessions found" %}';
        },
        onLoadSuccess: function(tableData) {}
    });
}

function loadUserTable(table, options = {}) {
    var columns = getLoanTableColumns();

    table.inventreeTable({
        url: '/plugin/loan/api/loanuser/',
        method: 'get',
        name: 'loanuser',
        columns: columns,
        sidePagination: 'server', // Allows the server to search for a RIN number (has to exactly match)
        uniqueId: 'pk',
        idField: 'pk',
        formatNoMatches: function() {
            return '{% trans "No loan users found" %}';
        },
        onLoadSuccess: function(tableData) {}
    });

}