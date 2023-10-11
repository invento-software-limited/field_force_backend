import frappe
from frappe.utils import cint, get_datetime, getdate, has_common, now_datetime, nowdate
from frappe.desk.doctype.dashboard_chart.dashboard_chart import (get_aggregate_function,
                                                                 get_heatmap_chart_config, get_result)

from frappe.utils import cint, get_datetime, getdate, has_common, now_datetime, nowdate
from frappe.utils.dashboard import cache_source
from frappe.utils.data import format_date
from frappe.utils.dateutils import (
	get_dates_from_timegrain,
	get_from_date_from_timespan,
	get_period,
	get_period_beginning,
)


@frappe.whitelist()
def get(
    chart_name=None,
    chart=None,
    no_cache=None,
    filters=None,
    from_date=None,
    to_date=None,
    timespan=None,
    time_interval=None,
    heatmap_year=None,
    refresh=None,
):

    if chart_name:
        chart = frappe.get_doc("Dashboard Chart", chart_name)
    else:
        chart = frappe._dict(frappe.parse_json(chart))

    heatmap_year = heatmap_year or chart.heatmap_year
    timespan = timespan or chart.timespan

    if timespan == "Select Date Range":
        if from_date and len(from_date):
            from_date = get_datetime(from_date)
        else:
            from_date = chart.from_date

        if to_date and len(to_date):
            to_date = get_datetime(to_date)
        else:
            to_date = get_datetime(chart.to_date)

    timegrain = time_interval or chart.time_interval
    filters = frappe.parse_json(filters) or frappe.parse_json(chart.filters_json)
    if not filters:
        filters = []

    # don't include cancelled documents
    filters.append([chart.document_type, "docstatus", "<", 2, False])

    if chart.chart_type == "Group By":
        chart_config = get_group_by_chart_config(chart, filters)
    else:
        if chart.type == "Heatmap":
            chart_config = get_heatmap_chart_config(chart, filters, heatmap_year)
        else:
            chart_config = get_chart_config(chart, filters, timespan, timegrain, from_date, to_date)

    return chart_config

def get_group_by_chart_config(chart, filters):
    aggregate_function = get_aggregate_function(chart.group_by_type)
    value_field = chart.aggregate_function_based_on or "1"
    group_by_field = chart.group_by_based_on
    doctype = chart.document_type

    data = frappe.get_all(
        doctype,
        fields=[
            f"{group_by_field} as name",
            f"{aggregate_function}({value_field}) as count",
        ],
        filters=filters,
        parent_doctype=chart.parent_document_type,
        group_by=group_by_field,
        order_by="count desc",
        ignore_ifnull=True,
    )

    if data:
        chart_config = {
            "labels": [item["name"] if item["name"] else "Not Specified" for item in data],
            "datasets": [{"name": chart.name, "values": [item["count"] for item in data]}],
        }

        return chart_config
    else:
        return None

def get_chart_config(chart, filters, timespan, timegrain, from_date, to_date):
    if not from_date:
        from_date = get_from_date_from_timespan(to_date, timespan)
        from_date = get_period_beginning(from_date, timegrain)
    if not to_date:
        to_date = now_datetime()

    doctype = chart.document_type
    datefield = chart.based_on
    value_field = chart.value_based_on or "1"
    from_date = from_date.strftime("%Y-%m-%d")
    to_date = to_date

    filters.append([doctype, datefield, ">=", from_date, False])
    filters.append([doctype, datefield, "<=", to_date, False])

    data = frappe.db.get_all(
        doctype,
        fields=[f"{datefield} as _unit", f"SUM({value_field})", "COUNT(*)"],
        filters=filters,
        group_by="_unit",
        order_by="_unit asc",
        as_list=True,
    )

    result = get_result(data, timegrain, from_date, to_date, chart.chart_type)

    return {
        "labels": [
            format_date(get_period(r[0], timegrain), parse_day_first=True)
            if timegrain in ("Daily", "Weekly")
            else get_period(r[0], timegrain)
            for r in result
        ],
        "datasets": [{"name": chart.name, "values": [r[1] for r in result]}],
    }
