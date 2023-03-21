frappe.views.TreeView = class CustomTreeView extends frappe.views.TreeView{
    rebuild_tree() {
		let me = this;
		let parent_field = "parent_" + me.doctype.toLowerCase().replace(/ /g, '_');

		if (me.doctype === "Employee") {
			parent_field = 'reports_to';
		}

		frappe.call({
			"method": "field_force.field_force.utils.nestedset.rebuild_tree",
			"args": {
				'doctype': me.doctype,
				'parent_field': parent_field,
			},
			"callback": function (r) {
				if (!r.exc) {
					me.make_tree();
				}
			}
		});
	}
}