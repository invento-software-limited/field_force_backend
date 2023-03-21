import frappe

@frappe.whitelist()
def rebuild_tree(doctype, parent_field):
	"""
	call rebuild_node for all root nodes
	"""

	# Check for perm if called from client-side
	if frappe.request and frappe.local.form_dict.cmd == "rebuild_tree":
		frappe.only_for("System Manager")

	meta = frappe.get_meta(doctype)
	if not meta.has_field("lft") or not meta.has_field("rgt"):
		frappe.throw(
			_("Rebuilding of tree is not supported for {}").format(frappe.bold(doctype)),
			title=_("Invalid Action"),
		)

	# get all roots
	frappe.db.auto_commit_on_many_writes = 1

	right = 1
	result = frappe.db.sql(
		"SELECT name FROM `tab%s` WHERE `%s`='' or `%s` IS NULL ORDER BY name ASC"
		% (doctype, parent_field, parent_field)
	)

	for r in result:
		right = rebuild_node(doctype, r[0], right, parent_field)

	frappe.db.auto_commit_on_many_writes = 0
	frappe.db.commit()


def rebuild_node(doctype, parent, left, parent_field):
	"""
	reset lft, rgt and recursive call for all children
	"""
	from frappe.utils import now

	n = now()

	# the right value of this node is the left value + 1
	right = left + 1

	# get all children of this node
	result = frappe.db.sql(
		"SELECT name FROM `tab{0}` WHERE `{1}`=%s".format(doctype, parent_field), (parent)
	)
	for r in result:
		right = rebuild_node(doctype, r[0], right, parent_field)

	# we've got the left value, and now that we've processed
	# the children of this node we also know the right value
	frappe.db.set_value(
		doctype, parent, {"lft": left, "rgt": right}, for_update=False, update_modified=False
	)

	# return the right value of this node + 1
	return right + 1