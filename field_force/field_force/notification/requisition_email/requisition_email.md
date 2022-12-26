<div class="ql-editor" data-gramm="false" contenteditable="true">
    <p>Dear Concern,<p>
    <p>A requsisition has been submitted and waiting for your decision. Please take action by clicking this link below -
    </p>
    <a href="{{frappe.utils.get_url_to_form(doc.doctype, doc.name)}}">
        <h3>Requisition - {{ doc.name }}</h2>
    </a>
    
    {% if doc.special_note %}
        {{ doc.special_note or "" }}
    {% endif %}

    <h3>Details:</h3>
    <table class="table table-bordered">
        <tbody>
            <tr>
                <td data-row="1">Partner Group</td>
                <td data-row="1">{{ doc.partner_group }}</td>
            </tr>
            <tr>
                <td data-row="1">Customer</td>
                <td data-row="1">{{ doc.customer }}</td>
            </tr>
            <tr>
                <td data-row="1">Distributor</td>
                <td data-row="1">{{ doc.distributor }}</td>
            </tr>
            <tr>
                <td data-row="3">Date</td>
                <td data-row="3">{{ doc.transaction_date }}</td>
            </tr>
            <tr>
                <td data-row="4">Delivery Date</td>
                <td data-row="4">{{ doc.delivery_date }}</td>
            </tr>
            <tr>
                <td data-row="5">Total Items</td>
                <td data-row="5">{{ doc.total_items }}</td>
            </tr>
            <tr>
                <td data-row="5">Total Quantity</td>
                <td data-row="5">{{ doc.total_qty }}</td>
            </tr>
            <tr>
                <td data-row="5">Sales Person</td>
                <td data-row="5">{{ doc.sales_person }}</td>
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
    <h3>{{ doc.company }}</h3>
</div>

{% if doc.requisition_excel_file %}
<div class="row">
    <a href="{{ frappe.get_url() }}{{ doc.requisition_excel }}">Requisition Excel File</a>
<div>
{% endif %}

{% if doc.purchase_order_file %}
    <div class="row mt-2">
        <a href="{{ frappe.get_url() }}{{ doc.purchase_order_file }}">Customer Purchase Order File</a>
    </div>
{% endif %}