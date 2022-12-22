<h4>{{ doc.company or "" }}</h4>

{{ doc.special_note or "" }}

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