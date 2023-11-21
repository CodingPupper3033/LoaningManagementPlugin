{% load i18n %}
{% load inventree_extras %}
{% load generic %}

function loadTestTable(table) {
    console.log('Loading test table');
    table.inventreeTable({
        url: '/plugin/loan/api/loansession/',
        method: 'get',
        name: 'testresult',
        columns: [
            {
                field: 'id',
                title: 'ID',
                visible: true,
                switchable: false,
            },
            {
                field: 'stock_item',
                title: 'Stock Item',
                visible: true
            },
            {
                field: 'loan_date',
                title: 'Loan Date',
                visible: true
            },
            {
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
            },
            {
                field: 'quantity',
                sortName: 'stock',
                title: 'Stock',
                sortable: true,
                formatter: function(value, row) {

                    var val = '';

                    if (row.stock_detail.serial && row.stock_detail.quantity == 1) {
                        // If there is a single unit with a serial number, use the serial number
                        val = '# ' + row.stock_detail.serial;
                    } else {
                        // Format floating point numbers with this one weird trick
                        val = formatDecimal(value);

                        if (row.stock_detail.part_detail && row.stock_detail.part_detail.units) {
                            val += ` ${row.stock_detail.part_detail.units}`;
                        }
                    }

                    return renderLink(val, `/stock/item/${row.stock_detail.pk}/`);
                }
            }

            ],
        queryFilters: {
            custom_actions: [
                {
                    actions: makeStockActions(table),
                    icon: 'fa-boxes',
                    title: '{% trans "Stock Actions" %}',
                    label: 'stock',
                }
            ]
        },
        onLoadSuccess: function(tableData) {
            console.log('Table loaded');
            console.log(tableData);
        }
    });
}

function loanSessionFields(options={}) {
     var fields = {
        stock: {

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
            model: 'user',
            secondary: {
                title: 'Add Part Category',
                fields: {

                }
            }
        },
        loan_user_detail__idn: {
            label: "IDN",
            type: "integer"
        },
        quantity: {

        },
        loan_date: {

        },
        due_date: {

        }
    }

    return fields;
}

function createNewLoanSession() {
    var url = '/plugin/loan/api/loansession/';
    var options = {};

    options.title = ' "Loan-out item"';

    options.method = 'POST';

    options.create = true;

    options.fields = loanSessionFields(options);

    constructForm(url, options);
}