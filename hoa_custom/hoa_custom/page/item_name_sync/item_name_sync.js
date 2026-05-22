frappe.pages["item-name-sync"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Item Name Sync",
		single_column: true,
	});
	new ItemNameSync(page);
};

const DOCTYPES = [
	{ label: "Purchase Order", table: "Purchase Order Item", type: "child" },
	{ label: "Purchase Invoice", table: "Purchase Invoice Item", type: "child" },
	{ label: "Purchase Receipt", table: "Purchase Receipt Item", type: "child" },
	{ label: "Material Request", table: "Material Request Item", type: "child" },
	{ label: "Sales Order", table: "Sales Order Item", type: "child" },
	{ label: "Sales Invoice", table: "Sales Invoice Item", type: "child" },
	{ label: "Delivery Note", table: "Delivery Note Item", type: "child" },
	{ label: "Stock Entry", table: "Stock Entry Detail", type: "child" },
	{ label: "Stock Ledger Entry", table: "Stock Ledger Entry", type: "direct" },
	{ label: "Bin", table: "Bin", type: "direct" },
];

class ItemNameSync {
	constructor(page) {
		this.page = page;
		this.all_checked = true;
		this.make();
		this.bind_events();
	}

	make() {
		const checklist_rows = DOCTYPES.map(
			(dt) => `
			<div class="checkbox" style="margin: 6px 0;">
				<label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
					<input type="checkbox" class="doctype-check" data-table="${dt.table}" checked />
					<span>
						<strong>${dt.label}</strong>
						<span class="text-muted" style="font-size:12px;">
							-> ${dt.table}${dt.type === "direct" ? " <em>(direct table)</em>" : ""}
						</span>
					</span>
				</label>
			</div>`
		).join("");

		$(this.page.body).append(`
			<div style="max-width:760px; margin:20px auto; padding:0 15px;">

				<div class="alert alert-warning" style="border-left:4px solid #e2a03f; padding:12px 16px; background:#fff8ee; border-radius:4px; margin-bottom:20px;">
					<strong>&#9888; Warning:</strong> Always take a database backup before running sync.
					Run <code>bench --site [site-name] backup</code> before proceeding.
				</div>

				<div class="frappe-card" style="padding:20px; margin-bottom:20px;">
					<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
						<h6 style="margin:0; font-weight:600;">Select Doctypes to Sync</h6>
						<button class="btn btn-xs btn-default" id="btn-toggle-all">Deselect All</button>
					</div>
					${checklist_rows}
				</div>

				<button class="btn btn-primary" id="btn-run-sync">
					&#9654; Run Sync
				</button>

				<div id="sync-progress" style="display:none; margin-top:20px;">
					<div class="progress" style="height:22px; border-radius:4px;">
						<div class="progress-bar progress-bar-striped active"
							role="progressbar" style="width:100%; line-height:22px;">
							Syncing item names&hellip;
						</div>
					</div>
				</div>

				<div id="sync-results" style="display:none; margin-top:20px;">
					<div class="frappe-card" style="padding:20px; margin-bottom:16px;">
						<h6 style="font-weight:600; margin-bottom:12px;">Rows Updated per Table</h6>
						<div id="results-summary"></div>
					</div>
					<div class="frappe-card" style="padding:20px;">
						<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
							<h6 style="font-weight:600; margin:0;">Items Synced</h6>
							<span id="items-count" class="text-muted" style="font-size:12px;"></span>
						</div>
						<div id="results-items" style="max-height:420px; overflow-y:auto;"></div>
					</div>
				</div>

			</div>
		`);
	}

	bind_events() {
		const self = this;

		$("#btn-toggle-all").on("click", function () {
			self.all_checked = !self.all_checked;
			$(".doctype-check").prop("checked", self.all_checked);
			$(this).text(self.all_checked ? "Deselect All" : "Select All");
		});

		$("#btn-run-sync").on("click", function () {
			const selected = [];
			$(".doctype-check:checked").each(function () {
				selected.push($(this).data("table"));
			});

			if (!selected.length) {
				frappe.msgprint(__("Please select at least one doctype to sync."));
				return;
			}

			frappe.confirm(
				__(
					"This will update <strong>item_name</strong> across {0} table(s) based on the current Item master. " +
						"Ensure you have a DB backup. Continue?",
					[selected.length]
				),
				() => self.run_sync(selected)
			);
		});
	}

	run_sync(selected) {
		$("#btn-run-sync").prop("disabled", true);
		$("#sync-progress").show();
		$("#sync-results").hide();

		frappe.call({
			method: "hoa_custom.hoa_custom.page.item_name_sync.item_name_sync.sync_item_names",
			args: { doctypes: selected },
			callback: (r) => {
				$("#sync-progress").hide();
				$("#btn-run-sync").prop("disabled", false);

				if (!r.message) return;

				const { summary, items_changed } = r.message;

				// Summary table
				const summaryRows = Object.entries(summary)
					.map(
						([table, count]) =>
							`<tr>
								<td>${table}</td>
								<td style="text-align:right;">
									<span class="badge ${count > 0 ? "badge-success" : ""}">${count}</span>
								</td>
							</tr>`
					)
					.join("");

				const total = Object.values(summary).reduce((a, b) => a + b, 0);

				$("#results-summary").html(`
					<table class="table table-bordered table-sm" style="margin-bottom:0;">
						<thead>
							<tr><th>Table</th><th style="text-align:right;">Rows Updated</th></tr>
						</thead>
						<tbody>${summaryRows}</tbody>
						<tfoot>
							<tr style="font-weight:600;">
								<td>Total</td>
								<td style="text-align:right;">${total}</td>
							</tr>
						</tfoot>
					</table>
				`);

				// Items changed table
				const n = items_changed.length;
				$("#items-count").text(`${n} unique item${n !== 1 ? "s" : ""}`);

				if (n === 0) {
					$("#results-items").html(
						`<p class="text-muted" style="margin:0;">All item names were already in sync.</p>`
					);
				} else {
					const itemRows = items_changed
						.map(
							(item) =>
								`<tr>
									<td style="font-family:monospace; white-space:nowrap;">${frappe.utils.escape_html(item.item_code)}</td>
									<td style="color:#c0392b;">${frappe.utils.escape_html(item.old_name)}</td>
									<td style="color:#27ae60;">${frappe.utils.escape_html(item.new_name)}</td>
								</tr>`
						)
						.join("");

					$("#results-items").html(`
						<table class="table table-bordered table-sm" style="margin-bottom:0;">
							<thead>
								<tr>
									<th>Item Code</th>
									<th>Old Name</th>
									<th>New Name (synced)</th>
								</tr>
							</thead>
							<tbody>${itemRows}</tbody>
						</table>
					`);
				}

				$("#sync-results").show();
				frappe.show_alert({ message: __("Sync complete!"), indicator: "green" });
			},
			error: () => {
				$("#sync-progress").hide();
				$("#btn-run-sync").prop("disabled", false);
			},
		});
	}
}