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
            model: 'user',
            label: 'Loanee',
            icon: 'fa-user',
           // secondary: {
           //     title: 'Search User',
           //     api_url: '/plugin/loan/api/loanuser/', // API endpoint for creating a new LoanUser - Shouldn't be hardcoded
           //     fields: loanUserFields()
           // },

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
 * defaults: a list of default values for fields, as desired.
 * @see LoanSessionList
 */
var handlinginprogress = false;
function createNewLoanSession(options = {},defaults = {}) {
    const url = '/plugin/loan/api/loansession/'; // API endpoint for creating a new LoanSession - Shouldn't be hardcoded

    options.title = '{% trans "Loan Stock Item" %}';

    options.method = 'POST';

    options.create = true;

    // Fields for the form
    options.fields = loanSessionFields(options);
    
    // get default values from arguments
    if(defaults){
        Object.keys(defaults).forEach(key => {
            options.fields[key].value = defaults[key]});
    }
    
    options.afterRender = function(fields,options) {
        userlookup_api_url = '{{ userlookup_api_url }}' || '{{ plugin.userlookup_api_url }}'
        if(userlookup_api_url){
            // disable enter from submitting the form.
            // disable previous keydown that enabled form submission with enter
            $(options.modal).off('keydown');
            // disable enter keydown on form.
            $(options.modal).on('keydown','input', function(e) {
                if(e.keyCode == 13) {
                    e.preventDefault();
                    return false;
                }
            });
            // Add a field to serve as badge scanner...
            $('#div_id_loan_user').eq(0).before(
                constructField('user_badge',{
                    label : "User ID or Badge",
                    required : false,
                    help_text : "Enter user ID here and press Enter OR Scan user ID here",
                    type : "string",
                }));
            // Now add callback from enter press on user badge to trigger user lookup
            $('#id_user_badge').keydown(function(e) {
                if(e.keyCode == 13) {
                   // if($('#id_user_badge').val().length == 8){ // validation of ID length
                        inventreeGet(
                            userlookup_api_url+$('#id_user_badge').val()+'/',
                            {}, {
                            success: function(data) {
                                console.log(data);
                                setRelatedFieldData('loan_user',data,{});
                            }});

                   // }
                }
            });
            //$('#id_loan_user').prop('disabled',true);
        }
       
    }


    options.onSuccess = function(respose) {
        // Set the table to refresh
        var table = options.table || '#loan-table';
        $(table).bootstrapTable('refresh');
    }

    constructForm(url, options);
}

// noinspection JSUnusedGlobalSymbols
/**
 * Launches a modal form to create a LoanUser
 */
function createNewLoanUser(options = {}) {
    const url = '/plugin/loan/api/loanuser/'; // API endpoint for creating a new LoanUser - Shouldn't be hardcoded

    options.title = '{% trans "Loan User Item" %}';

    options.method = 'POST';

    options.create = true;

    // Fields for the form
    options.fields = loanUserFields(options);

    constructForm(url, options);
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

function makeLoanActions(table) {
    let actions = [
        {
            icon: 'fa-check-square',
            title: '{% trans "Return Item" %}',
            label: 'return',
            callback: function(data) {
                returnLoanSessions(table, data);
            }
        }
    ];

    return actions;
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
    if( !options.params.hasOwnProperty('stock_detail') ){
        options.params.stock_detail = false;
    }
    if( !options.params.hasOwnProperty('user_detail') ){
        options.params.user_detail = false;
    }
    if( !options.hasOwnProperty('showreturn') ){
        options.showreturn = true;
    }

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
                    actions: makeLoanActions(table),
                    icon: 'fa-box',
                    title: '{% trans "Loan Actions" %}',
                    label: 'loan-actions',
                },
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
    const columns = [
        {
            checkbox: true,
            title: '{% trans "Select" %}',
            searchable: false,
            switchable: false,
        },
        {
            field: 'pk',
            title: 'ID',
            visible: false,
            switchable: false,
        }
    ];

    if(options.params.stock_detail){
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
    }

    if( options.params.user_detail ){
        col = {
            field: 'first_name',
            title: 'First Name',
            visible: true,
            formatter: function(value, row) {
                // noinspection JSUnresolvedReference
                return row.loan_user_detail.first_name;
            }
        }

        if (!options.params.ordering) {
            col['sortable'] = true;
        }

        columns.push(col);

        col = {
            field: 'last_name',
            title: 'Last Name',
            visible: true,
            formatter: function(value, row) {
                // noinspection JSUnresolvedReference
                return row.loan_user_detail.last_name;
            }
        }

        if (!options.params.ordering) {
            col['sortable'] = true;
        }

        columns.push(col);

        col = {
            field: 'e-mail',
            title: 'E-mail',
            visible: true,
            formatter: function(value, row) {
                // noinspection JSUnresolvedReference
                return row.loan_user_detail.username;
            }
        }

        if (!options.params.ordering) {
            col['sortable'] = true;
        }

        columns.push(col);
    }

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

    if(options.showreturn){
        // Returned
        col = {
            field: 'returned_date',
            title: 'Returned Date',
            visible: true,
            formatter: function(value,row) {
                if(value){
                    return renderDate(value);
                }else{
                    if(options.loan_button) {
                        $(options.loan_button).attr('disabled',true);
                    }
                    var bReturn = getReturnButton(row.pk);
                    return `<div class='btn-group' role='group'>${bReturn}</div>`;
                }
            }
        }
   
        if (!options.params.ordering) {
            col['sortable'] = true;
        }
   
        columns.push(col);
    }

    // Edit button
    col = {
        field: 'edit',
        title: '',
        visible: true,
        formatter: function(value,row){
            var bEdit = getLoanEditButton(row.pk);
            return `<div class='btn-group float-right' role='group'>${bEdit}</div>`;
        }
    }
    col['sortable'] = false;
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

    table.on('click','.return-loan',function() {
        returnLoanSession(table,this.getAttribute("pk"));
    });

    table.on('click','.edit-loan',function() {
        window.alert("Edit loan functionality not implemented yet!");
    });
}

/**
 * Creates a modal to return multiple stock items
 */
function returnLoanSessions(table, items, options={}) {
    // ID Values of the not returned items
    let id_values = [];

    // Beginning of the modal HTML
    let html = `
        <table class='table table-striped table-condensed' id='loan-adjust-table'>
        <thead>
        <tr>
            <th>{% trans "Part" %}</th>
            <th>{% trans "Stock" %}</th>
            <th>{% trans "User" %}</th>
            <th></th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        `;

    items.forEach(function(item) {
        // Skip items that have already been returned
        if (item["returned"]) {
            return;
        }

        // Get data for the table row
        const pk = item.pk;
        const stock_detail = item.stock_detail;
        const part_detail = stock_detail.part_detail;

        // Get the stock item serial number or quantity
        let serial_column = '';
        // Does the stock have a serial number?
        if (stock_detail.serial && stock_detail.quantity === 1) {
            // If there is a single unit with a serial number, use the serial number
            serial_column = '# ' + stock_detail.serial;
        } else {
            // Format floating point numbers with this one weird trick
            serial_column = formatDecimal(stock_detail.quantity);

            if (stock_detail.part_detail && stock_detail.part_detail.units) {
                serial_column += ` ${stock_detail.part_detail.units}`;
            }
        }

        let actionInput = constructField(
            `returned_date_${pk}`,
            {
                type: 'date',
                value: moment().format('YYYY-MM-DD'),
                min_value: item.loan_date,
                required: true,
            },
            {
                hideLabels: true,
            }
        );

        let buttons = wrapButtons(makeRemoveButton(
            'button-loan-session-remove',
            pk,
            '{% trans "Remove stock item" %}',
        ));

        // noinspection JSUnresolvedReference
        const thumb = thumbnailImage(part_detail.thumbnail || part_detail.image);

        // Add this item as a row in the table
        // noinspection JSUnresolvedReference
        html += `
            <tr id='loan_session_${pk}' class='loan-session-row'>
                <td id='part_${pk}'>${thumb} ${part_detail.full_name}</td>
                <td id='stock_${pk}'>${serial_column}</td>
                <td id='user_${pk}'>${item.loan_user_detail.username}</td>
                <td id='returned_date_${pk}'>${actionInput}</td>
                <td id='buttons_${pk}'>${buttons}</td>
            </tr>`;

        // Add the pk to the list of items to be returned
        id_values.push(item.pk);
    });

    // Validate there is at least one session selected/selectable
    if (id_values.length == 0) {
        showAlertDialog(
            '{% trans "Select Stock Items" %}',
            '{% trans "Select one or more stock items that have not been returned yet." %}'
        );
        return;
    }

    // Add the end of the table
    html += `</tbody></table>`;

    // URL for the return API
    const url = '/plugin/loan/api/loansession/return/'; // TODO URL Still should not be hardcoded
    // Create the form
    constructForm(url, {
        method: 'POST',
        fields: {},
        preFormContent: html,
        confirm: true,
        confirmMessage: '{% trans "Confirm Return" %}',
        title: '{% trans "Return Stock Items" %}',
        afterRender: function(fields, opts) {
            // Add button callbacks to remove rows
            $(opts.modal).find('.button-loan-session-remove').click(function () {
                const pk = $(this).attr('pk');

                $(opts.modal).find(`#loan_session_${pk}`).remove();
            });
        },
        onSubmit: function(fields, opts) {
            // Extract data elements from the form
            const data = {
                items: [],
            };

            items.forEach(function(item) {
                var pk = item.pk;

                // Does the row exist in the form?
                var row = $(opts.modal).find(`#loan_session_${pk}`);

                if (row.exists()) {
                    const returned_date = getFormFieldValue(`returned_date_${pk}`, {}, opts);

                    data.items.push({
                        pk: pk,
                        returned_date: returned_date,
                    });
                }
            });

            inventreePut(
                url,
                data,
                {
                    method: 'POST',
                    success: function(response) {
                        // Hide the modal
                        $(opts.modal).modal('hide');

                        // Refresh the table
                        $(table).bootstrapTable('refresh');
                    },
                    error: function(xhr) {
                        switch (xhr.status) {
                        case 400:
                            handleFormErrors(xhr.responseJSON, fields, opts);
                            break;
                        default:
                            $(opts.modal).modal('hide');
                            showApiError(xhr, opts.url);
                            break;
                        }
                    }
                }
            );
        },
        onSuccess: function(response, opts) {
            console.log("Success");
        }
    });
}

// noinspection JSUnusedGlobalSymbols
/**
 * Loads a loanee user table
 * @param table HTML table to load the loanee user table into
 * @param options Options for the table
 * Options:
 * - url: URL to load the table from
 * - params: Query parameters when requesting loanee users
 * - disableFilters: Disable the filters for the table
 */
function loadLoaneeTable(table, options = {}) {
    options.params = options.params || {};

    let filters = {};

    if (!options.disableFilters) {
        const filterTarget = options["filterTarget"] || '#filter-list-loanee';
        const filterKey = options["filterKey"] || options.name || 'loanee';

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


    // Total items out
    col = {
        field: 'loaned',
        title: 'Loaned',
        visible: true,
        searchable: true,
    }

    if (!options.params.ordering) {
        col['sortable'] = true;
    }

    columns.push(col);

    // Overdue items
    col = {
        field: 'overdue',
        title: 'Overdue',
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
        url: options.url || '/plugin/loan/api/loanee/',
        method: 'get',
        name: 'loanee',
        original: options.params,
        sidePagination: 'server', // Allows the server to check for RIN number (since it should be hidden from the user)
        queryParams: filters,
        columns: columns,
        uniqueId: 'pk',
        idField: 'pk',
        formatNoMatches: function() {
            return '{% trans "No active loans" %}';
        }
    });

}

/**
 * Creates a modal to return stock items
 */
function returnLoanSessions(table, items, options={}) {
    // ID Values of the not returned items
    let id_values = [];

    // Beginning of the modal HTML
    let html = `
        <table class='table table-striped table-condensed' id='loan-adjust-table'>
        <thead>
        <tr>
            <th>{% trans "Part" %}</th>
            <th>{% trans "Stock" %}</th>
            <th>{% trans "User" %}</th>
            <th></th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        `;

    items.forEach(function(item) {
        // Skip items that have already been returned
        if (item["returned"]) {
            return;
        }

        // Get data for the table row
        const pk = item.pk;
        const stock_detail = item.stock_detail;
        const part_detail = stock_detail.part_detail;

        // Get the stock item serial number or quantity
        let serial_column = '';
        // Does the stock have a serial number?
        if (stock_detail.serial && stock_detail.quantity === 1) {
            // If there is a single unit with a serial number, use the serial number
            serial_column = '# ' + stock_detail.serial;
        } else {
            // Format floating point numbers with this one weird trick
            serial_column = formatDecimal(stock_detail.quantity);

            if (stock_detail.part_detail && stock_detail.part_detail.units) {
                serial_column += ` ${stock_detail.part_detail.units}`;
            }
        }

        let actionInput = constructField(
            `returned_date_${pk}`,
            {
                type: 'date',
                value: moment().format('YYYY-MM-DD'),
                min_value: item.loan_date,
                required: true,
            },
            {
                hideLabels: true,
            }
        );

        let buttons = wrapButtons(makeRemoveButton(
            'button-loan-session-remove',
            pk,
            '{% trans "Remove stock item" %}',
        ));

        // noinspection JSUnresolvedReference
        const thumb = thumbnailImage(part_detail.thumbnail || part_detail.image);

        // Add this item as a row in the table
        // noinspection JSUnresolvedReference
        html += `
            <tr id='loan_session_${pk}' class='loan-session-row'>
                <td id='part_${pk}'>${thumb} ${part_detail.full_name}</td>
                <td id='stock_${pk}'>${serial_column}</td>
                <td id='user_${pk}'>${item.loan_user_detail.username}</td>
                <td id='returned_date_${pk}'>${actionInput}</td>
                <td id='buttons_${pk}'>${buttons}</td>
            </tr>`;

        // Add the pk to the list of items to be returned
        id_values.push(item.pk);
    });

    // Validate there is at least one session selected/selectable
    if (id_values.length == 0) {
        showAlertDialog(
            '{% trans "Select Stock Items" %}',
            '{% trans "Select one or more stock items that have not been returned yet." %}'
        );
        return;
    }

    // Add the end of the table
    html += `</tbody></table>`;

    // URL for the return API
    const url = '/plugin/loan/api/loansession/return/'; // TODO URL Still should not be hardcoded
    // Create the form
    constructForm(url, {
        method: 'POST',
        fields: {},
        preFormContent: html,
        confirm: true,
        confirmMessage: '{% trans "Confirm Return" %}',
        title: '{% trans "Return Stock Items" %}',
        afterRender: function(fields, opts) {
            // Add button callbacks to remove rows
            $(opts.modal).find('.button-loan-session-remove').click(function () {
                const pk = $(this).attr('pk');

                $(opts.modal).find(`#loan_session_${pk}`).remove();
            });
        },
        onSubmit: function(fields, opts) {
            // Extract data elements from the form
            const data = {
                items: [],
            };

            items.forEach(function(item) {
                var pk = item.pk;

                // Does the row exist in the form?
                var row = $(opts.modal).find(`#loan_session_${pk}`);

                if (row.exists()) {
                    const returned_date = getFormFieldValue(`returned_date_${pk}`, {}, opts);

                    data.items.push({
                        pk: pk,
                        returned_date: returned_date,
                    });
                }
            });

            inventreePut(
                url,
                data,
                {
                    method: 'POST',
                    success: function(response) {
                        // Hide the modal
                        $(opts.modal).modal('hide');

                        // Refresh the table
                        $(table).bootstrapTable('refresh');
                    },
                    error: function(xhr) {
                        switch (xhr.status) {
                        case 400:
                            handleFormErrors(xhr.responseJSON, fields, opts);
                            break;
                        default:
                            $(opts.modal).modal('hide');
                            showApiError(xhr, opts.url);
                            break;
                        }
                    }
                }
            );
        },
        onSuccess: function(response, opts) {
            console.log("Success");
        }
    });
}

/**
 * Creates a modal to return a single stock item via pk value
 */
function returnLoanSession(table,item, options={}) {
    // Beginning of the modal HTML
    let actionInput = constructField(
        `returned_date_ret`,
        {
            type: 'date',
            value: moment().format('YYYY-MM-DD'),
            min_value: item.loan_date,
            required: true,
        },
        {
            hideLabels: true,
        }
    );

    let html = `
        <table class='table table-striped table-condensed' id='loan-adjust-table'>
        <thead>
        <tr>
            <th>{% trans "Part" %}</th>
            <th>{% trans "Stock Item" %}</th>
            <th>{% trans "First Name" %}</th>
            <th>{% trans "Last Name" %}</th>
            <th>{% trans "E-mail" %}</th>
            <th>{% trans "Loan Date" %}</th>
            <th>{% trans "Due Date" %}</th>
            <th>{% trans "Return Date" %}</th>
            <th></th>
            <th></th>
        </tr>
        </thead>
        <tbody>
            <tr id='loan_session' class='loan-session-row'>
                <td id='part_ret'></td>
                <td id='stock_ret'></td>
                <td id='first_ret'></td>
                <td id='last_ret'></td>
                <td id='email_ret'></td>
                <td id='loandate_ret'></td>
                <td id='duedate_ret'></td>
                <td id='returned_date_ret'>${actionInput}</td>
            </tr>
         </tbody></table>`;


    // URL for the return API
    const url = '/plugin/loan/api/loansession/return/'; // TODO URL Still should not be hardcoded
    // Create the form
    constructForm(url, {
        method: 'POST',
        fields: {},
        preFormContent: html,
        confirm: true,
        confirmMessage: '{% trans "Confirm Return" %}',
        title: '{% trans "Return Stock Item" %}',
        afterRender: function(fields, opts) {
            inventreeGet(`/plugin/loan/api/loansession/${item}/?stock_detail=true&user_detail=true`,{},{ // TODO URL, also check search parameters (better way to format?)
                success: function(data) {
                    $('#part_ret').text(data.stock_detail.part_detail.name);
                    $('#stock_ret').text(data.stock_detail.serial);
                    $('#first_ret').text(data.loan_user_detail.first_name);
                    $('#last_ret').text(data.loan_user_detail.last_name);
                    $('#email_ret').text(data.loan_user_detail.email);
                    $('#loandate_ret').text(data.loan_date);
                    $('#duedate_ret').text(data.due_date);
                }
            });
        },
        onSubmit: function(fields, opts) {
            // Extract data elements from the form
            const data = {
                items: [],
            };
            data.items.push({
                pk: item,
                returned_date: getFormFieldValue('returned_date_ret',{},opts),
            });

            inventreePut(
                url,
                data,
                {
                    method: 'POST',
                    success: function(response) {
                        // Hide the modal
                        $(opts.modal).modal('hide');

                        // Refresh the table
                        $(table).bootstrapTable('refresh');
                    },
                    error: function(xhr) {
                        switch (xhr.status) {
                        case 400:
                            handleFormErrors(xhr.responseJSON, fields, opts);
                            break;
                        default:
                            $(opts.modal).modal('hide');
                            showApiError(xhr, opts.url);
                            break;
                        }
                    }
                }
            );
        },
        onSuccess: function(response, opts) {
            console.log("Success");
        }
    });
}
/**
 * Returns the html for a edit button (templated from notification.js)
 *
 * arguments:
 * pk: primary key of the loan session
**/
function getLoanEditButton(pk) {
    let bIcon = 'fas fa-pen-square';
    
    return `<button title={% trans "Edit Loan" %} class='edit-loan btn btn-smbtn-outline-secondary float-left' type='button' pk='${pk}' target='loanedit'><span class='${bIcon}'></span></button>`;
}

/**
 * Returns the html for a loan return button (templated from notification.js)
 *
 * arguments:
 * pk: primary key of the loan session
**/
function getReturnButton(pk) {
    let bIcon = 'fas fa-pen-square';
    
    return `<button type='button' class='return-loan btn btn-success' id='loan-return' pk='${pk}'} target='loanreturn'>
                <span class='fas fa-share-square'></span> {% trans "Return" %}
            </button>`;
}

/**
 * Check if script is loaded from a stock item page. If so, load tracking 
 * loan tracking information into "Loaning" panel
**/

{% if item %} // probably a better way to do this... `item` exists on stock pages and not loan pages.
              // use this to differentiate which page this script is loaded on.
    $(document).ready(function(){
        loadLoanTable($('#stockitem-table'),{
                params: {
                    stock: {{ item.pk }},
                    stock_detail: false,
                    user_detail: true,
                    ordering: '-due_date'
                },
                loan_button: '#loan-create', 
        });
        $('#loan-create').click(function() {
            createNewLoanSession({table:'#stockitem-table'},{stock:'{{ item.pk }}'});
        });
    });

{% endif %}
