{% load i18n %}
{% load inventree_extras %}
{% load generic %}

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
        sortable: true,
        formatter: function(value, row) {
            return shortenString(row.loan_user_detail.username);
        }
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

function loadLoanTable(table, options={}) {
    var col = null;
    var columns = getTrackingTableColumns();

    const filterTarget = options.filterTarget || '#filter-list-loan';
    const filterKey = options.filterKey || options.name || 'loan';

    let filters = loadTableFilters(filterKey, options.params); // Filtering doesn't do much as we can't override InvenTree's filtering

    // Setup buttons above the table
    setupFilterList(filterKey, table, filterTarget, {
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
                            const overdue = !table.bootstrapTable('getOptions').query_params['overdue'];
                            let options = {}

                            if (overdue) {
                                options['overdue'] = 'true';
                            }

                            reloadTableFilters(table, options, {});
                        }
                    },
                    {
                        icon: 'fa-calendar',
                        title: '{% trans "Loaned" %}',
                        label: 'current',
                        callback: function(data) {
                            const current = !table.bootstrapTable('getOptions').query_params['current'];

                            let options = {}

                            if (current) {
                                options['current'] = 'true';
                            }

                            reloadTableFilters(table, options, {});
                        }
                    },
                    {
                        icon: 'fa-calendar-check',
                        title: '{% trans "Returned" %}',
                        label: 'returned',
                        callback: function(data) {
                            console.log('Returned');
                            const returned = !table.bootstrapTable('getOptions').query_params['returned'];

                            let options = {}

                            if (returned) {
                                options['returned'] = 'true';
                            }

                            reloadTableFilters(table, options, {});
                        }
                    }
                ],
                icon: 'fa-filter',
                title: '{% trans "Loan Filters" %}',
                label: 'loan',
            }
        ]
    });

    filters = Object.assign(filters, options.params);

    table.inventreeTable({
        url: '/plugin/loan/api/loansession/',
        method: 'get',
        name: 'loan',
        queryParams: filters,
        columns: columns,
        onLoadSuccess: function(tableData) {
        }
    });
}

