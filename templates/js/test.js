

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
                    console.log(row.part_id)
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
        onLoadSuccess: function(tableData) {
            console.log('Table loaded');
            console.log(tableData);
        }
    });
}

function createNewLoanSession() {
    var url = '/plugin/loan/api/loansession/';
    var options = {};

    options.method = 'POST';
    options.create = true;

    options.fields = {
        stock: {

        },
        loan_user: {

        },
        quantity: {

        },
        loan_date: {

        },
        due_date: {

        }
    }

    constructForm(url, options);
}