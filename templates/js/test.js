

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
            }

            ],
        onLoadSuccess: function(tableData) {
            console.log('Table loaded');
            console.log(tableData);
        }
    });
}