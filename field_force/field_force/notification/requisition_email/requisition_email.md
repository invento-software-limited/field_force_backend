<div>
    <p>Dear Concern,<p>
    <p style="margin-top:5px;">A requisition has been submitted. Please check the requisition by clicking this link below -
    </p>
    <a href="{{frappe.utils.get_url_to_form(doc.doctype, doc.name)}}">
        <h3>Requisition - {{ doc.name }}</h2>
    </a>
    
    <h3>Details:</h3>
    <table class="table table-bordered">
        <tbody>
            {% if doc.partner_group %}
                <tr>
                    <td data-row="1">Partner Group</td>
                    <td data-row="1">{{ doc.partner_group or "" }}</td>
                </tr>
            {% endif %}
            
            <tr>
                <td data-row="1">Customer</td>
                <td data-row="1"><b>{{ doc.customer or "" }}</b></td>
            </tr>
            
            {% if doc.customer_id %}
                <tr>
                    <td data-row="1">Customer ID</td>
                    <td data-row="1">{{ doc.customer_id or "" }}</td>
                </tr>
            {% endif %}
            
            {% if doc.distributor %}
                <tr>
                    <td data-row="1">Distributor</td>
                    <td data-row="1">{{ doc.distributor or "" }}</td>
                </tr>
            {% endif %}
            
            <tr>
                <td data-row="3">Date</td>
                <td data-row="3">{{ doc.transaction_date.strftime("%d-%m-%Y") }}</td>
            </tr>
            <tr>
                <td data-row="4">Delivery Date</td>
                <td data-row="4">{{ doc.delivery_date.strftime("%d-%m-%Y") }}</td>
            </tr>
            <tr>
                <td data-row="5">Total Items</td>
                <td data-row="5">{{ doc.total_items }}</td>
            </tr>
            <tr>
                <td data-row="5">Total Quantity</td>
                <td data-row="5">{{ doc.total_qty or 0 }}</td>
            </tr>
            <tr>
                <td data-row="5">Grand Total</td>
                <td data-row="5">{{ frappe.format_value(doc.grand_total, {'fieldtype': 'Currency'}) }}</td>
            </tr>
            <tr>
                <td data-row="5">Sales Person</td>
                <td data-row="5">{{ doc.sales_person or "" }}</td>
            </tr>

            {% if doc.po_no %}
                <tr>
                    <td data-row="5">PO Number</td>
                    <td data-row="5">{{ doc.po_no }}</td>
                </tr>
            {% endif %}
            {% if doc.po_date %}
                <tr>
                    <td data-row="5">PO Number</td>
                    <td data-row="5">{{ doc.po_date }}</td>
                </tr>
            {% endif %}
        </tbody>
    </table>
</div>

{% if doc.requisition_excel_file %}
    <br>
    <div class="row mt-4">
        <a href="{{ frappe.get_url() }}{{ doc.requisition_excel }}" target="_blank">Requisition Excel File</a>
    <div>
{% endif %}

{% if doc.purchase_order_file %}
    <br>
    <div class="row mt-4">
        <a href="{{ frappe.get_url() }}{{ doc.purchase_order_file }}" target="_blank">Customer Purchase Order File</a>
    </div>
{% endif %}


{% if doc.special_note %}
    <br>
    <div class="mt-4">
        <label sytle="font-size: 14px;"><b>Special Note:</b></label>
        <div>
            {{ doc.special_note or "" }}
        </div>
    </div>
    
{% endif %}

<div class="mt-4">
    <h3>{{ doc.company }}</h3>
</div>